from typing import Annotated
from typing import Any
from typing import Optional
from typing import ParamSpec
from typing import get_args
from typing import get_origin


def resolve_annotated_type(cls: type) -> Optional[tuple[Any, list]]:
    origin: ParamSpec = get_origin(cls)
    if origin is Annotated:
        args: tuple[Any, ...] = get_args(cls)
        base_type, metadata = args[0], args[1:]
        return base_type, list(metadata)
    elif hasattr(cls, "__value__"):
        return resolve_annotated_type(cls.__value__)
    return None
