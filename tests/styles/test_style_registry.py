"""StyleRegistry tests."""

import pytest

from md2docx.styles.definition import StyleDefinition
from md2docx.styles.registry import DuplicateStyleError, StyleRegistry


def test_register_get_has():
    registry = StyleRegistry()
    definition = StyleDefinition(semantic_id="normal", ooxml_id="Normal", name="Normal")
    registry.register(definition)
    assert registry.has("normal")
    assert registry.get("normal") == definition


def test_duplicate_registration_rejected():
    registry = StyleRegistry()
    definition = StyleDefinition(semantic_id="normal", ooxml_id="Normal", name="Normal")
    registry.register(definition)
    with pytest.raises(DuplicateStyleError):
        registry.register(definition)


def test_ooxml_id_lookup():
    registry = StyleRegistry()
    registry.register(StyleDefinition(semantic_id="quote", ooxml_id="Quote", name="Quote"))
    assert registry.ooxml_id("quote") == "Quote"
