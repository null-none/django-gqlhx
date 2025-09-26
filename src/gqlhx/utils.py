from importlib import import_module
from typing import Any


def import_string(dotted_path: str) -> Any:
    """Import a dotted path (like 'myapp.schema.schema') and return the object."""
    try:
        module_path, attr = dotted_path.rsplit(".", 1)
    except ValueError as exc:
        raise ImportError(f"{dotted_path} isn't a valid module path") from exc
    module = import_module(module_path)
    try:
        return getattr(module, attr)
    except AttributeError as exc:
        raise ImportError(f"Module '{module_path}' does not define '{attr}'") from exc
