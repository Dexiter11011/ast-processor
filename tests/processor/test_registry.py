"""HandlerRegistry tests."""

import pytest

from md2docx.processor.element_handler import ElementHandler
from md2docx.processor.errors import UnsupportedNodeError
from md2docx.processor.registry import HandlerRegistry


class _StubHandler:
    def process(self, node, context, processor) -> None:
        pass


def test_register_and_get():
    registry = HandlerRegistry()
    handler = _StubHandler()
    assert registry.register("paragraph", handler) is registry
    assert registry.get("paragraph") is handler


def test_register_chain():
    registry = HandlerRegistry()
    result = registry.register("a", _StubHandler()).register("b", _StubHandler())
    assert result is registry
    assert registry.has("a") and registry.has("b")


def test_registered_types():
    registry = HandlerRegistry()
    registry.register("paragraph", _StubHandler())
    assert registry.registered_types() == frozenset({"paragraph"})


def test_get_missing_raises():
    registry = HandlerRegistry()
    with pytest.raises(UnsupportedNodeError, match="unsupported AST node: paragraph"):
        registry.get("paragraph")


def test_has():
    registry = HandlerRegistry()
    assert registry.has("paragraph") is False
    registry.register("paragraph", _StubHandler())
    assert registry.has("paragraph") is True
