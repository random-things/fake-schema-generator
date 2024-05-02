from collections.abc import Sequence
from decimal import Decimal
from typing import get_args

type SupportsSum = int | float | Decimal


def typed_sum(sequence: Sequence[SupportsSum]) -> SupportsSum | None:
    if not sequence:
        return None

    supported_types = get_args(SupportsSum.__value__)
    if any(type(i) not in supported_types for i in sequence):
        raise TypeError(f"Unsupported type in sequence: {sequence}")

    accumulator = sequence[0]

    if len(sequence) == 1:
        return accumulator

    for i in sequence[1:]:
        accumulator += i

    return accumulator
