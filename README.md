# Fake Schema Generator

## Requirements

* Python 3.12+
  * dataclasses
  * typing (`TypeAliasType`)
* [faker](https://github.com/joke2k/faker)

## Example

See `example/run.py` for a full example. See `tests/FakeSchemaGenerator_test.py` for more examples.

## How does it work?

The `FakeSchemaGenerator` class takes a schema and generates data based on that schema. The schema is defined using the
new style of type annotations. The `FakeSchemaGenerator` class uses the `faker` library to generate the data. When you
register models with the `FakeSchemaGenerator` class, it creates a directed acyclic graph (DAG) of the fields and the
order in which they need to be faked. Then, when you call the `generate_from_dag` method, it can create a data set that
is valid for your schema across all models.

The resolution of the DAG is what enables the `ReferenceProvider` and `CalculateProvider` classes to work. The 
`ReferenceProvider` class generates a value based on a reference to another table, and the `CalculateProvider` class
calculates the value for a field depending on other field values. You could absolutely do this by hand, e.g.,

```python
from faker import Faker

fake = Faker()

class OrderProduct:
    def __init__(self):
        self.order_id = fake.random_int()
        self.product_id = fake.random_int()
        self.quantity = fake.random_int()
        self.unit_price = fake.pyfloat(positive=True, min_value=0.01, max_value=100, right_digits=2)
        self.total = self.unit_price * self.quantity
```

But that becomes a lot more fragile if, for instance, you also have a `Payment` table that needs to reflect the order's
total, or you're pulling the `unit_price` from a `Product` table. The `FakeSchemaGenerator` class allows you to define
the schema and let it handle the rest rather than having to manually keep track of the order of dependencies in your
schema.

Another neat trick is that `FakeSchemaGenerator` tries to track down models that you've referenced, even if they aren't
registered with the `FakeSchemaGenerator` class. If you look at the example provided in the Questions section, you'll
see that only the `Order` class is registered with the `FakeSchemaGenerator` class. The `Customer` class is not
registered, but the `FakeSchemaGenerator` detects the reference to the `Customer` class, registers it, and regenerates
the DAG in order to resolve the `CustomerID` field in the `Order` class to the `id` field in the `Customer` class.

Furthermore, even if there's a cyclic model dependency, as long as there's not a cyclic field dependency, the
`FakeSchemaGenerator` class can resolve the DAG. For instance, if you have an `Order` class that contains a `total` and
an `OrderProduct` class that contains `order_id`, `quantity`, and `unit_price`, you'll see that `Order` depends on
`OrderProduct` to be able to calculate `Order.total`, but `OrderProduct` depends on `Order` to have an `order_id`.
Because the DAG is generated at the field level, `order_id` will be filled in with a value, allowing `OrderProduct` to
reference `Order` and finally allowing `Order` to calculate `Order.total` from
`OrderProduct.quantity * OrderProduct.unit_price`.

## Providers

### `CalculateProvider`

A provider for `faker` that calculates the value for a field depending on other field values. For instance, if you have
an `Order` table with a `total` field and an `OrderProduct` table with `quantity` and `price` fields, you can use the
`CalculateProvider` to calculate the `total` field in the `Order` table based on the `quantity` and `price` fields in
the `OrderProduct` table.

```python
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
```

This performs something similar to the following SQL query:

```sql
SELECT SUM(unit_price * quantity) AS total
FROM OrderProduct
WHERE order_id = Order.id
```

### `ReferenceProvider`

A provider for `faker` that generates a value based on a reference to another table. For instance, if you have a
`Customer` table with an `id` field and an `Order` table with a `customer_id` field, you can use the `ReferenceProvider`
to generate a `customer_id` in the `Order` table that references an `id` in the `Customer` table.

```python
...
type CustomerID = Annotated[int, FakeType("reference", model="Customer", field="id")]
...
class Order:
    ...
    customer_id: CustomerID
```

### `SequentialNumberProvider`

A provider for `faker` that generates a sequential number based on a namespace. For instance, if you have a `Customer`
table with an `id` field, you can use the `SequentialNumberProvider` to generate a unique `id` for each `Customer`.
Basically the equivalent of an auto-incrementing primary key in a database.

```python
...
type CustomerRowID = Annotated[int, FakeType("sequential_number", namespace="customer")]
...
class Customer:
    id: CustomerRowID
```


## Types

### `FakeType`

A type annotation that specifies the type of data to generate. The `FakeType` annotation takes a `provider` argument
that specifies the `faker` function to call. Any parameters passed to the `FakeType` annotation are passed to the
`provider` function.

### `ValueOf`

A type annotation that specifies the value of a field to use in a calculation. The `ValueOf` annotation takes a `field`
argument that specifies the field to use. This is useful when you want to reference the value of another field and not a
literal value.

```python
type UnitPrice = Annotated[
    float,
    FakeType(
        "reference",
        model="Product",
        field="price",
        conditions=[SchemaCondition("product_id", operator.eq, ValueOf("product_id"))],
    ),
]
```

This is essentially the same as the following SQL query:

```sql
SELECT price
FROM Product
WHERE product_id = OrderProduct.product_id
```

If you didn't specify the `ValueOf` annotation, the query would look like this:

```sql
SELECT price
FROM Product
WHERE product_id = 'product_id'
```

### `SchemaCondition`

A type annotation that specifies a condition to use in a calculation. The `SchemaCondition` annotation takes a `field`,
`operator`, and `value` argument that specifies the field to compare, the operator to use, and the value to compare. An
example of its use can be seen above in the `ValueOf` annotation.

## Questions

### Why do I need Fake Schema Generator?

Faker is great for generating random values for test data, but it can be a bit difficult to generate a large amount of
data with a consistent schema. This script allows you to supply a Python schema based on the `TypeAliasType` style of type
annotations and generate data based on that schema.

### I have no clue what you're talking about.

That's okay! Here's an example. If you want to generate a list of customers, Faker makes that pretty easy:

```python
from faker import Faker


class Customer:
    def __init__(self, name: str, email: str, phone: str):
        self.name = name
        self.email = email
        self.phone = phone

fake = Faker()
customers = [Customer(fake.name(), fake.email(), fake.phone_number()) for _ in range(3)]

for customer in customers:
    print(customer.__dict__)

# Output:
# {'name': 'Joseph Stone', 'email': 'griffithkerry@example.com', 'phone': '001-529-833-9036x656'}
# {'name': 'Susan Robinson', 'email': 'danielle32@example.org', 'phone': '(358)307-2793'}
# {'name': 'Michael Robinson', 'email': 'ataylor@example.net', 'phone': '714.356.0962x352'}
```

But these days, who's generating lists in a vacuum? They're typically part of a relational schema and you want all of
the data to be generated at once and to be internally consistent. So now let's take a slightly larger example:

```python
from faker import Faker


class Customer:
    def __init__(self, customer_id: int, name: str, email: str, phone: str):
        self.id = customer_id
        self.name = name
        self.email = email
        self.phone = phone

        
class Orders:
    def __init__(self, order_id: int, customer_id: int, order_date: str, total: float):
        self.id = order_id
        self.customer_id = customer_id
        self.order_date = order_date
        self.total = total


fake = Faker()
customers = [Customer(i+1, fake.name(), fake.email(), fake.phone_number()) for i in range(3)]
orders = [Orders(i+1,
                 fake.random_int(1, 3),
                 fake.date_this_year(),
                 fake.pyfloat(positive=True, min_value=0.01, max_value=100, right_digits=2)) for i in range(3)]

for customer in customers:
    print(customer.__dict__)

for order in orders:
    print(order.__dict__)

# Output:
# {'id': 1, 'name': 'Jason Woodard', 'email': 'tracywood@example.org', 'phone': '(730)331-1654x559'}
# {'id': 2, 'name': 'Jamie Fox', 'email': 'mary70@example.com', 'phone': '001-836-405-8348x13785'}
# {'id': 3, 'name': 'Maria Walsh', 'email': 'pamela08@example.net', 'phone': '(214)564-9714'}
# {'id': 1, 'customer_id': 1, 'order_date': datetime.date(2024, 2, 17), 'total': 14.88}
# {'id': 2, 'customer_id': 3, 'order_date': datetime.date(2024, 4, 8), 'total': 62.42}
# {'id': 3, 'customer_id': 3, 'order_date': datetime.date(2024, 4, 14), 'total': 38.27}
```

Now we're getting a little more cumbersome. We have to generate the customers first, then generate the orders, and then
we have to make sure that the `customer_id` in the `Orders` class matches the `id` in the `Customer` class. This is
where Fake Schema Generator comes in. We can define the schema for the data we want to generate and then generate it all
at once:

```python
import datetime

from dataclasses import dataclass
from typing import Annotated

from fake_schema_generator import FakeSchemaGenerator
from fake_schema_generator import FakeType


type CustomerRowID = Annotated[int, FakeType("sequential_number", namespace="customer")]
type Name = Annotated[str, FakeType("name")]
type Email = Annotated[str, FakeType("email")]
type Phone = Annotated[str, FakeType("phone_number")]

type OrderRowID = Annotated[int, FakeType("sequential_number", namespace="order")]
type CustomerID = Annotated[int, FakeType("reference", model="Customer", field="id")]
type OrderDate = Annotated[datetime.datetime, FakeType("date_time_this_year")]
type OrderTotal = Annotated[float, FakeType("pyfloat", positive=True, min_value=0.01, max_value=100, right_digits=2)]


@dataclass
class Customer:
    id: CustomerRowID
    name: Name
    email: Email
    phone: Phone


@dataclass
class Order:
    id: OrderRowID
    customer_id: CustomerID
    order_date: OrderDate
    total: OrderTotal


fake = FakeSchemaGenerator()
fake._register(Order)

for i in range(3):
    fake.generate_from_dag()

for i in range(3):
    print(fake._raw_data["Customer"][i])

for i in range(3):
    print(fake._raw_data["Order"][i])

# Output:
# Customer(id=1, name='Shane Gross', email='lopezchristopher@example.org', phone='(826)717-3333')
# Customer(id=2, name='Michael Castro', email='oshelton@example.com', phone='3272489689')
# Customer(id=3, name='Christine Hill', email='hhughes@example.org', phone='761.743.7006x37338')
# Order(id=1, customer_id=1, order_date=datetime.datetime(2024, 1, 30, 13, 30, 8), total=71.6)
# Order(id=2, customer_id=2, order_date=datetime.datetime(2024, 4, 14, 13, 45, 29), total=85.27)
# Order(id=3, customer_id=2, order_date=datetime.datetime(2024, 1, 19, 8, 54, 26), total=63.97)
```

### Isn't that a lot of extra code for the same result?

Yes, but no matter how large your schema is, you can generate all of the data through type annotations. It lets you
separate your schema from your data generation, which can be useful if you're generating a lot of data or you just like
maintaining a clean separation of concerns.