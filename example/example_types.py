import datetime
import operator
from typing import Annotated

from fake_schema_generator import FakeType
from fake_schema_generator import SchemaCondition
from fake_schema_generator import ValueOf

type CustomerRowID = Annotated[int, FakeType("sequential_number", namespace="customer")]
type FirstName = Annotated[str, FakeType("first_name")]
type LastName = Annotated[str, FakeType("last_name")]
type EmailAddress = Annotated[str, FakeType("email")]
type PhoneNumber = Annotated[str, FakeType("phone_number")]
type StreetAddress = Annotated[str, FakeType("street_address")]

type OrderRowID = Annotated[int, FakeType("sequential_number", namespace="order")]
type CustomerID = Annotated[int, FakeType("reference", model="Customer", field="customer_id")]
type OrderDate = Annotated[datetime.datetime, FakeType("date_time_this_year")]
type TotalAmount = Annotated[
    float,
    FakeType(
        "calculate",
        model="OrderProduct",
        field="order_id",
        value=ValueOf("order_id"),
        fields=["unit_price", "quantity"],
        row_op=operator.mul,
        col_op=operator.add,
    ),
]
type OrderStatus = Annotated[
    str,
    FakeType("random_element", elements=("Pending", "Shipped", "Delivered", "Returned")),
]

type ProductRowID = Annotated[int, FakeType("sequential_number", namespace="product")]
type ProductName = Annotated[str, FakeType("product_name")]
type ProductDescription = Annotated[str, FakeType("text")]
type ProductPrice = Annotated[
    float,
    FakeType("pyfloat", positive=True, min_value=0.01, max_value=100, right_digits=2),
]
type ProductStockQuantity = Annotated[int, FakeType("random_int", min=0, max=100)]

type OrderProductRowID = Annotated[int, FakeType("sequential_number", namespace="order_details")]
type OrderID = Annotated[int, FakeType("reference", model="Order", field="order_id")]
type ProductID = Annotated[int, FakeType("reference", model="Product", field="product_id")]
type Quantity = Annotated[int, FakeType("random_int", min=1, max=10)]
type UnitPrice = Annotated[
    float,
    FakeType(
        "reference",
        model="Product",
        field="price",
        conditions=[SchemaCondition("product_id", operator.eq, ValueOf("product_id"))],
    ),
]

type PaymentRowID = Annotated[int, FakeType("sequential_number", namespace="payment")]
type PaymentDate = Annotated[datetime.datetime, FakeType("date_time_this_year")]
type PaymentAmount = Annotated[
    float,
    FakeType(
        "reference",
        model="Order",
        field="total_amount",
        conditions=[SchemaCondition("order_id", operator.eq, ValueOf("order_id"))],
    ),
]
type PaymentMethod = Annotated[str, FakeType("random_element", elements=("Credit Card", "Debit Card", "PayPal"))]
type PaymentStatus = Annotated[str, FakeType("random_element", elements=("Pending", "Paid", "Failed"))]
