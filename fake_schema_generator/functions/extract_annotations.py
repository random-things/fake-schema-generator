from typing import Any

from .resolve_annotated_type import resolve_annotated_type


def extract_annotations(cls: type):
    annotations: dict[str, Any] = {}
    for field_name, field_type in cls.__annotations__.items():
        actual_type: tuple[Any, list] = resolve_annotated_type(field_type)
        if actual_type:
            base_type, metadata = actual_type
            annotations[field_name] = {"type": base_type, "metadata": metadata}
        else:
            annotations[field_name] = {"type": field_type, "metadata": []}
    return annotations
