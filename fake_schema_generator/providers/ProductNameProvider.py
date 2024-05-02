from faker.providers import BaseProvider


class ProductNameProvider(BaseProvider):
    def __init__(self, generator):
        super().__init__(generator)

    def product_name(self) -> str:
        return f"{self.generator.word(part_of_speech='adjective')} {self.generator.word(part_of_speech='noun')}"
