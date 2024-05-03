from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Optional

from fake_schema_generator.operators import noop

from .SchemaReferenceBaseProvider import SchemaReferenceBaseProvider


class CalculateProvider(SchemaReferenceBaseProvider):
    """
    CalculateProvider is a Faker provider that wraps a call to the same function in `FakeSchemaGenerator` in order to
    calculate values for one model based on values in another.
    """

    def __init__(self, fake_generator, schema_generator):
        super().__init__(fake_generator, schema_generator)
        self.reference_functions = {"calculate"}

    def calculate(
        self,
        source_model: dataclass,
        model: type[dataclass],
        field: str,
        value: Any,
        fields: list[str],
        row_op: Optional[Callable] = noop,
        col_op: Optional[Callable] = noop,
    ) -> Any:
        """
        Wraps a call to the same function in `FakeSchemaGenerator`

        Raises:
            ValueError: If the schema generator is not set.
        """
        if self.schema_generator is None:
            raise ValueError("Schema generator not set")

        return self.schema_generator.calculate(source_model, model, field, value, fields, row_op, col_op)
