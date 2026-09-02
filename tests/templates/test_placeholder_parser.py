"""Unit tests for TemplatePlaceholderParser."""

from __future__ import annotations

import pytest

from md2docx.templates.errors import TemplatePlaceholderError
from md2docx.templates.placeholder_parser import TemplatePlaceholderParser


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("{{content}}", "content"),
        ("{{ title }}", "title"),
        ("{{  author  }}", "author"),
        ("{{date}}", "date"),
    ],
)
def test_parse_valid_standalone_placeholder(text: str, expected: str):
    assert TemplatePlaceholderParser.parse_standalone(text) == expected


def test_non_placeholder_paragraph_returns_none():
    assert TemplatePlaceholderParser.parse_standalone("Hello world") is None


@pytest.mark.parametrize(
    "text",
    [
        "Project: {{title}}",
        "{{ user.name }}",
        "{{foo | upper}}",
        "{{foo.bar}}",
        "{{}}",
        "{{123name}}",
        "{{ name-with-dash }}",
    ],
)
def test_invalid_or_inline_placeholder_raises(text: str):
    with pytest.raises(TemplatePlaceholderError):
        TemplatePlaceholderParser.parse_standalone(text)


def test_normalize_name_strips_whitespace():
    assert TemplatePlaceholderParser.normalize_name("{{  title  }}") == "title"
