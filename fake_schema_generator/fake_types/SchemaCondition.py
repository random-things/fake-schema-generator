from dataclasses import dataclass
from typing import Any
from typing import Callable


@dataclass
class SchemaCondition:
    field: str
    comparison: Callable[[Any, Any], bool]
    value: Any
