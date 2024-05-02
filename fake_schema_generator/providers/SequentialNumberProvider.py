from faker.providers import BaseProvider


class SequentialNumberProvider(BaseProvider):
    def __init__(self, generator):
        super().__init__(generator)
        self.numbers: dict[str, int] = {}

    def sequential_number(self, namespace: str = "default") -> int:
        if namespace not in self.numbers:
            self.numbers[namespace] = 0
        self.numbers[namespace] += 1
        return self.numbers[namespace]

    def reset_sequence(self, namespace: str = "default"):
        if namespace in self.numbers:
            del self.numbers[namespace]
