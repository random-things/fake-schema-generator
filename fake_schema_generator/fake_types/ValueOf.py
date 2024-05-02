class ValueOf:
    def __init__(self, field: str):
        self.field = field

    def __repr__(self):
        return f"ValueOf({self.field})"
