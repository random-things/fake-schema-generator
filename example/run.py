import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from example_classes import Customer
from example_classes import Order
from example_classes import OrderProduct
from example_classes import Payment
from example_classes import Product

from fake_schema_generator import FakeSchemaGenerator


def fake_load():
    sg = FakeSchemaGenerator()
    sg.register(Customer)
    sg.register(Product)
    sg.register(Order)
    sg.register(OrderProduct)
    sg.register(Payment)

    for _ in range(0, 100):
        sg.generate()

    print(sg.data())


if __name__ == "__main__":
    fake_load()
