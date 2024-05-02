from collections.abc import Sequence
from decimal import Decimal
from typing import get_args

type SupportsProduct = int | float | Decimal


def typed_product(sequence: Sequence[SupportsProduct]) -> SupportsProduct | None:
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
