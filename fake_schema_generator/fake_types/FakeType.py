class FakeType:
    def __init__(self, type_: str, **kwargs):
        self.type = type_
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        return self.type

    def __repr__(self):
        return f"FakeType(type={self.type}, kwargs={self.kwargs})"
