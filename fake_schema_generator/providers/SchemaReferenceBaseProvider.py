from faker.providers import BaseProvider


class SchemaReferenceBaseProvider(BaseProvider):
    def __init__(self, fake_generator, fake_schema_generator):
        super().__init__(fake_generator)
        self.schema_generator = fake_schema_generator
        self.reference_functions = set()
