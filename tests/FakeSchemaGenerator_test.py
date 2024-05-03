import operator
from dataclasses import dataclass
from typing import Annotated

import pytest

from fake_schema_generator import FakeSchemaGenerator
from fake_schema_generator import FakeType
from fake_schema_generator import SchemaCondition
from fake_schema_generator import ValueOf
from fake_schema_generator import typed_product
from fake_schema_generator import typed_sum


@pytest.fixture
def schema_generator():
    sg = FakeSchemaGenerator()
    sg._fake.seed_instance(0)
    return sg


@dataclass
class Customer:
    id: Annotated[int, FakeType("sequential_number", namespace="customer")]
    name: Annotated[str, FakeType("name")]


@dataclass
class CustomerDetails:
    id: Annotated[int, FakeType("sequential_number", namespace="customer_details")]
    customer_id: Annotated[int, FakeType("reference", model="Customer", field="id")]
    email: Annotated[str, FakeType("email")]


@dataclass
class Product:
    id: Annotated[int, FakeType("sequential_number", namespace="product")]
    name: Annotated[str, FakeType("product_name")]
    description: Annotated[str, FakeType("text")]
    price: Annotated[float, FakeType("pyfloat", positive=True, min_value=0.01, max_value=100, right_digits=2)]
    stock_quantity: Annotated[int, FakeType("random_int", min=0, max=100)]
    inventory_value: Annotated[
        float,
        FakeType(
            "calculate",
            model="Product",
            field="id",
            value=ValueOf("id"),
            fields=["price", "stock_quantity"],
            row_op=typed_product,
            col_op=typed_sum,
        ),
    ]


@dataclass
class Order:
    id: Annotated[int, FakeType("sequential_number", namespace="order")]
    customer_id: Annotated[int, FakeType("reference", model="Customer", field="id")]
    order_date: Annotated[str, FakeType("date_time_this_year")]
    total_amount: Annotated[
        float,
        FakeType(
            "calculate",
            model="OrderProduct",
            field="order_id",
            value=ValueOf("id"),
            fields=["unit_price", "quantity"],
            row_op=typed_product,
            col_op=typed_sum,
        ),
    ]
    order_status: Annotated[str, FakeType("random_element", elements=("Pending", "Shipped", "Delivered", "Returned"))]


@dataclass
class OrderProduct:
    id: Annotated[int, FakeType("sequential_number", namespace="order_details")]
    order_id: Annotated[int, FakeType("reference", model="Order", field="id")]
    product_id: Annotated[int, FakeType("reference", model="Product", field="id")]
    quantity: Annotated[int, FakeType("random_int", min=1, max=10)]
    unit_price: Annotated[
        float,
        FakeType(
            "reference",
            model="Product",
            field="price",
            conditions=[SchemaCondition("product_id", operator.eq, ValueOf("id"))],
        ),
    ]


class TestFakeSchemaGenerator:
    def test_exists(self, schema_generator):
        assert schema_generator is not None

    def test_basic_schema(self, schema_generator):
        schema_generator.register(Customer)
        schema_generator._build_model_dependencies()
        assert schema_generator._models == {"Customer": Customer}
        assert schema_generator._model_dependencies == {"Customer": set()}
        assert schema_generator._field_dependencies == {("Customer", "id"): set(), ("Customer", "name"): set()}
        assert schema_generator._field_dag == [
            ("Customer", "id"),
            ("Customer", "name"),
        ]
        schema_generator.generate_from_dag()
        assert schema_generator._raw_data["Customer"] == [
            Customer(id=1, name="Norma Fisher"),
        ]

    def test_pulls_in_related_schema(self, schema_generator):
        schema_generator.register(CustomerDetails)
        schema_generator._build_model_dependencies()
        assert "Customer" in schema_generator._models

    def test_related_schema(self, schema_generator):
        schema_generator.register(CustomerDetails)
        schema_generator._build_model_dependencies()
        assert schema_generator._models == {"Customer": Customer, "CustomerDetails": CustomerDetails}
        assert schema_generator._model_dependencies == {"Customer": set(), "CustomerDetails": {"Customer"}}
        assert schema_generator._field_dependencies == {
            ("Customer", "id"): set(),
            ("Customer", "name"): set(),
            ("CustomerDetails", "id"): set(),
            ("CustomerDetails", "customer_id"): {("Customer", "id")},
            ("CustomerDetails", "email"): set(),
        }
        assert schema_generator._field_dag == [
            ("Customer", "id"),
            ("Customer", "name"),
            ("CustomerDetails", "id"),
            ("CustomerDetails", "email"),
            ("CustomerDetails", "customer_id"),
        ]

    def test_calculating_schema(self, schema_generator):
        schema_generator.register(Product)
        schema_generator._build_model_dependencies()
        schema_generator.generate_from_dag()
        assert schema_generator._raw_data["Product"] == [
            Product(
                id=1,
                name="physical chain",
                description="Whole magazine truth stop whose.\nThrough despite cause cause believe son would mouth."
                " Total financial role together range line beyond its. Policy daughter need kind miss "
                "artist truth trouble.",
                price=69.57,
                stock_quantity=11,
                inventory_value=765.27,
            ),
        ]

    def test_schema_with_circular_model_dependencies(self, schema_generator):
        schema_generator.register(OrderProduct)
        schema_generator._build_model_dependencies()
        assert all(model in schema_generator._models for model in ["Product", "Order", "OrderProduct", "Customer"])
        # Because CustomerDetails isn't registered or referenced by any of the tables in the schema, it shouldn't be
        # included in the schema.
        assert "CustomerDetails" not in schema_generator._models
        assert schema_generator._model_dependencies == {
            "Product": {"Product"},
            "Order": {"Customer", "OrderProduct"},
            "OrderProduct": {"Order", "Product"},
            "Customer": set(),
        }
        assert schema_generator._field_dependencies == {
            ("Product", "id"): set(),
            ("Product", "name"): set(),
            ("Product", "description"): set(),
            ("Product", "price"): set(),
            ("Product", "stock_quantity"): set(),
            ("Product", "inventory_value"): {("Product", "id"), ("Product", "price"), ("Product", "stock_quantity")},
            ("Order", "id"): set(),
            ("Order", "customer_id"): {("Customer", "id")},
            ("Order", "order_date"): set(),
            ("Order", "total_amount"): {
                ("OrderProduct", "unit_price"),
                ("OrderProduct", "quantity"),
                ("OrderProduct", "order_id"),
            },
            ("Order", "order_status"): set(),
            ("OrderProduct", "id"): set(),
            ("OrderProduct", "order_id"): {("Order", "id")},
            ("OrderProduct", "product_id"): {("Product", "id")},
            ("OrderProduct", "quantity"): set(),
            ("OrderProduct", "unit_price"): {("Product", "price")},
            ("Customer", "id"): set(),
            ("Customer", "name"): set(),
        }
        # We can't test the full DAG because the order of the fields isn't guaranteed, only that dependencies are
        # satisfied.
        dag = schema_generator._field_dag
        assert dag.index(("Product", "inventory_value")) > dag.index(("Product", "price"))
        assert dag.index(("Product", "inventory_value")) > dag.index(("Product", "stock_quantity"))
        assert dag.index(("Product", "inventory_value")) > dag.index(("Product", "id"))
        assert dag.index(("Order", "total_amount")) > dag.index(("OrderProduct", "unit_price"))
        assert dag.index(("Order", "total_amount")) > dag.index(("OrderProduct", "quantity"))
        assert dag.index(("Order", "total_amount")) > dag.index(("OrderProduct", "order_id"))
        assert dag.index(("Order", "customer_id")) > dag.index(("Customer", "id"))
        assert dag.index(("OrderProduct", "unit_price")) > dag.index(("Product", "price"))
        assert dag.index(("OrderProduct", "order_id")) > dag.index(("Order", "id"))
        assert dag.index(("OrderProduct", "product_id")) > dag.index(("Product", "id"))
        schema_generator.generate_from_dag()
        # Similarly, we can't test the full structure of each generated object because even though the seed is fixed,
        # the order of generation affects the state of the random generator and because the order of generation isn't
        # fixed due to the DAG ordering, we can only test that the calculated and relational values are correct.
        data = schema_generator._raw_data
        assert data["Product"][0].inventory_value == data["Product"][0].price * data["Product"][0].stock_quantity
        assert data["OrderProduct"][0].unit_price == data["Product"][0].price
        assert data["Order"][0].total_amount == data["OrderProduct"][0].unit_price * data["OrderProduct"][0].quantity
        assert data["Order"][0].customer_id == data["Customer"][0].id
        assert data["OrderProduct"][0].order_id == data["Order"][0].id
        assert data["OrderProduct"][0].product_id == data["Product"][0].id
