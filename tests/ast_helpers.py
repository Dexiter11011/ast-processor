"""Serialize AST dataclasses to JSON-compatible dicts for snapshot tests."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import Any


def ast_to_dict(node: Any) -> Any:
    if is_dataclass(node):
        if hasattr(node, "type"):
            result: dict[str, Any] = {"type": node.type}
            for field in fields(node):
                if field.name == "type":
                    continue
                value = getattr(node, field.name)
                if field.name == "footnotes" and not value:
                    continue
                result[field.name] = ast_to_dict(value)
            return result
        return {field.name: ast_to_dict(getattr(node, field.name)) for field in fields(node)}
    if isinstance(node, list):
        return [ast_to_dict(item) for item in node]
    if hasattr(node, "value"):  # Enum
        return node.value
    return node
