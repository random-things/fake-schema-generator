from dataclasses import dataclass
from typing import Any
from typing import Optional

from ..fake_types import SchemaCondition
from .SchemaReferenceBaseProvider import SchemaReferenceBaseProvider


class ReferenceProvider(SchemaReferenceBaseProvider):
    """
    ReferenceProvider is a Faker provider that wraps a call to the same function in `FakeSchemaGenerator` in order to
    generate references to other models.
    """

    def __init__(self, fake_generator, schema_generator):
        super().__init__(fake_generator, schema_generator)
        self.reference_functions = {"reference"}

    def reference(
        self,
        source_model: dataclass,
        model: type[dataclass],
        field: Optional[str] = None,
        conditions: Optional[list["SchemaCondition"]] = None,
    ) -> Any:
        """
        Wraps a call to the same function in `FakeSchemaGenerator`

        Raises:
            ValueError: If the schema generator is not set.
        """
        if self.schema_generator is None:
            raise ValueError("Schema generator not set")

        return self.schema_generator.reference(source_model, model, field, conditions)
