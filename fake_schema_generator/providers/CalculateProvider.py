import dataclasses
from typing import Any
from typing import Callable
from typing import Optional

from fake_schema_generator.operators import noop

from .SchemaReferenceBaseProvider import SchemaReferenceBaseProvider


class CalculateProvider(SchemaReferenceBaseProvider):
    def __init__(self, fake_generator, schema_generator):
        super().__init__(fake_generator, schema_generator)
        self.reference_functions = {"calculate"}

    def calculate(
        self,
        source_model: dataclasses.dataclass,
        model: dataclasses.dataclass,
        field: str,
        value: Any,
        fields: list[str],
        row_op: Optional[Callable] = noop,
        col_op: Optional[Callable] = noop,
    ) -> Any:
        if self.schema_generator is None:
            raise ValueError("Schema generator not set")

        return self.schema_generator.calculate(source_model, model, field, value, fields, row_op, col_op)
