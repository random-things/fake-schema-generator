from typing import Optional

from faker.providers import BaseProvider


class SequentialNumberProvider(BaseProvider):
    """
    A Faker provider for generating namespaced sequential numbers, like those that would be typically be used for
    auto-incrementing primary keys in a database.

    Attributes:
        generator (Faker): The Faker instance that this provider is attached to.
        numbers (dict[str, int]): A dictionary of the current number for each namespace.
    """

    def __init__(self, generator):
        super().__init__(generator)
        self.numbers: dict[str, int] = {}

    def sequential_number(self, namespace: str = "default") -> int:
        """
        Generate a sequential number for the given namespace.

        Args:
            namespace (str): The namespace to generate a sequential number for, defaults to `"default"`.

        Returns:
            int: The next number in the sequence for the given namespace.
        """
        if namespace not in self.numbers:
            self.numbers[namespace] = 0
        self.numbers[namespace] += 1
        return self.numbers[namespace]

    def reset_sequence(self, namespace: Optional[str] = None):
        """
        Reset the sequence for the given namespace, or all namespaces if `namespace` is None.

        Args:
            namespace (Optional[str]): The namespace to reset the sequence for, defaults to `None`. If `None`, all
            sequences will be reset.
        """
        if namespace in self.numbers:
            del self.numbers[namespace]
