import pytest
from faker import Faker

from fake_schema_generator import SequentialNumberProvider


@pytest.fixture
def faker():
    fake = Faker()
    fake.add_provider(SequentialNumberProvider)
    return fake


class TestSequentialNumberProvider:
    def test_basic_sequence(self, faker):
        assert faker.sequential_number() == 1
        assert faker.sequential_number() == 2
        assert faker.sequential_number() == 3

    def test_namespace_sequence(self, faker):
        assert faker.sequential_number("test") == 1
        assert faker.sequential_number("test") == 2
        assert faker.sequential_number("test") == 3
        assert faker.sequential_number("other") == 1
        assert faker.sequential_number("test") == 4
        assert faker.sequential_number("other") == 2

    def test_reset_sequence(self, faker):
        assert faker.sequential_number("test") == 1
        assert faker.sequential_number("test") == 2
        assert faker.sequential_number("test") == 3
        faker.reset_sequence("test")
        assert faker.sequential_number("test") == 1
        assert faker.sequential_number("test") == 2
        assert faker.sequential_number("test") == 3
