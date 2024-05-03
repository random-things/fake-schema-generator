from collections.abc import Sequence
from decimal import Decimal
from typing import get_args

type SupportsSum = int | float | Decimal


def typed_sum(sequence: Sequence[SupportsSum]) -> SupportsSum | None:
    """
    Sum the numbers in the sequence.

    Types:
        SupportsSum: int | float | Decimal

    Args:
        sequence (Sequence[SupportsSum]): A sequence of numbers to add together.

    Returns:
        SupportsSum: The sum of the numbers in the sequence.

    Raises:
        TypeError: If the sequence contains an unsupported type.
    """
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
