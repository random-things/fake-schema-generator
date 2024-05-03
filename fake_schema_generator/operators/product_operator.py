from collections.abc import Sequence
from decimal import Decimal
from typing import get_args

type SupportsProduct = int | float | Decimal


def typed_product(sequence: Sequence[SupportsProduct]) -> SupportsProduct | None:
    """
    Multiply the numbers in the sequence together.

    Types:
        SupportsProduct: int | float | Decimal

    Args:
        sequence (Sequence[SupportsProduct]): A sequence of numbers to multiply.

    Returns:
        SupportsProduct: The product of the numbers in the sequence.

    Raises:
        TypeError: If the sequence contains an unsupported type.
    """
    if not sequence:
        return None

    supported_types = get_args(SupportsProduct.__value__)
    if any(type(i) not in supported_types for i in sequence):
        raise TypeError(f"Unsupported type in sequence: {sequence}")

    accumulator = sequence[0]

    if len(sequence) == 1:
        return accumulator

    for i in sequence[1:]:
        accumulator *= i

    return accumulator
