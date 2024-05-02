import pytest

from fake_schema_generator import typed_product as product


class TestProductOperator:
    def test_product_of_single_value(self):
        for i in range(4):
            assert product([i - 1]) == i - 1

    def test_product_of_no_values(self):
        assert product([]) is None

    def test_product_of_multiple_values(self):
        assert product([1, 2, 3, 4]) == 24
        assert product([1, -1, 1]) == -1
        assert product([-1, -1, 1]) == 1

    def test_product_of_floats(self):
        assert product([1.5, 2.5, 3.5]) == 13.125
        assert product([1.5, -1.5, 1.5]) == -3.375
        assert product([-1.5, -1.5, 1.5]) == 3.375

    def test_product_of_mixed_types(self):
        assert product([2, 2.5, 3]) == 15

        with pytest.raises(TypeError):
            product([2, 2.5, "3"])

    def test_product_of_none(self):
        with pytest.raises(TypeError):
            product([None])

        with pytest.raises(TypeError):
            product([None, None])
