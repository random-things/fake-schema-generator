from faker.providers import BaseProvider


class ProductNameProvider(BaseProvider):
    """
    A Fake provider for generating product names.
    """

    def __init__(self, generator):
        super().__init__(generator)

    def product_name(self) -> str:
        """
        Generate a product name.

        Returns:
            str: A product name.
        """
        return f"{self.generator.word(part_of_speech='adjective')} {self.generator.word(part_of_speech='noun')}"
