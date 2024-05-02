import pytest

from fake_schema_generator import typed_sum


class TestTypedSumOperator:
    def test_typed_sum_of_single_value(self):
        for i in range(4):
            assert typed_sum([i - 1]) == i - 1

    def test_typed_sum_of_no_values(self):
        assert typed_sum([]) is None

    def test_typed_sum_of_multiple_values(self):
        assert typed_sum([1, 2, 3, 4]) == 10
        assert typed_sum([1, -1, 1]) == 1
        assert typed_sum([-1, -1, 1]) == -1

    def test_typed_sum_of_floats(self):
        assert typed_sum([1.5, 2.5, 3.5]) == 7.5
        assert typed_sum([1.5, -1.5, 1.5]) == 1.5
        assert typed_sum([-1.5, -1.5, 1.5]) == -1.5

    def test_typed_sum_of_mixed_types(self):
        assert typed_sum([2, 2.5, 3]) == 7.5

        with pytest.raises(TypeError):
            typed_sum([2, 2.5, "3"])

    def test_typed_sum_of_none(self):
        with pytest.raises(TypeError):
            typed_sum([None])
