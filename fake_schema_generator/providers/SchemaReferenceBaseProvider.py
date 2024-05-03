from faker.providers import BaseProvider


class SchemaReferenceBaseProvider(BaseProvider):
    """
    A base class for providers that reference other models in a schema. This class is not meant to be used directly, but
    rather to be subclassed by other providers.

    Attributes:
        schema_generator: The schema generator to use for reference functions.
        reference_functions: The names of reference functions to provide to the `FakeSchemaGenerator`.
    """

    def __init__(self, fake_generator, fake_schema_generator):
        super().__init__(fake_generator)
        self.schema_generator = fake_schema_generator
        self.reference_functions = set()
