import dataclasses
from typing import Any
from typing import Optional

from ..fake_types import SchemaCondition
from .SchemaReferenceBaseProvider import SchemaReferenceBaseProvider


class ReferenceProvider(SchemaReferenceBaseProvider):
    def __init__(self, fake_generator, schema_generator):
        super().__init__(fake_generator, schema_generator)
        self.reference_functions = {"reference"}

    def reference(
        self,
        source_model: dataclasses.dataclass,
        model: dataclasses.dataclass,
        field: Optional[str] = None,
        conditions: Optional[list["SchemaCondition"]] = None,
    ) -> Any:
        if self.schema_generator is None:
            raise ValueError("Schema generator not set")

        return self.schema_generator.reference(source_model, model, field, conditions)
