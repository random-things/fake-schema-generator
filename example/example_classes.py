from dataclasses import dataclass

from example_types import *


@dataclass
class Customer:
    customer_id: CustomerRowID
    first_name: FirstName
    last_name: LastName
    email: EmailAddress
    phone: PhoneNumber
    address: StreetAddress


@dataclass
class Order:
    order_id: OrderRowID
    customer_id: CustomerID
    order_date: OrderDate
    total_amount: TotalAmount
    status: OrderStatus


@dataclass
class Product:
    product_id: ProductRowID
    name: ProductName
    description: ProductDescription
    price: ProductPrice
    stock_quantity: ProductStockQuantity


@dataclass
class OrderProduct:
    order_details_id: OrderProductRowID
    order_id: OrderID
    product_id: ProductID
    quantity: Quantity
    unit_price: UnitPrice


@dataclass
class Payment:
    payment_id: PaymentRowID
    order_id: OrderID
    payment_date: PaymentDate
    amount: PaymentAmount
    payment_method: PaymentMethod
    status: PaymentStatus
