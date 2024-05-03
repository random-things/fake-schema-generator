from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from typing import Optional
from typing import get_type_hints


def dataclass_to_interface(cls: type[dataclass]) -> type[dataclass]:
    """
    Convert a dataclass to an interface by making all fields optional and defaulting to None

    Args:
        cls: type[dataclass]: A dataclass to convert to an interface

    Returns:
        type[dataclass]: A new dataclass type named f"I{cls}" with all fields made optional and defaulting to None
    """
    new_attrs = {"__annotations__": {}}
    type_hints = get_type_hints(cls)
    for f in fields(cls):
        original_type = type_hints[f.name]
        optional_type = Optional[original_type]
        new_attrs["__annotations__"][f.name] = optional_type
        new_attrs[f.name] = field(default=None)

    new_cls = type(f"I{cls.__name__}", (cls,), new_attrs)
    return dataclass(new_cls)
