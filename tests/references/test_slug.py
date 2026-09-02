"""Slug generation unit tests."""

from md2docx.references.slug import disambiguate_slug, heading_plain_text, slugify
from md2docx.ast.types import Emphasis, Heading, Strong, Text


def test_slugify_spaces_and_punctuation():
    assert slugify("Hello World") == "hello-world"
    assert slugify("API Reference!") == "api-reference"


def test_slugify_unicode():
    assert slugify("Über Café") == "uber-cafe"


def test_slugify_empty_fallback():
    assert slugify("***") == "section"
    assert slugify("") == "section"


def test_disambiguate_duplicate_slugs():
    used: dict[str, int] = {}
    assert disambiguate_slug("introduction", used) == "introduction"
    assert disambiguate_slug("introduction", used) == "introduction-1"
    assert disambiguate_slug("introduction", used) == "introduction-2"


def test_heading_plain_text_ignores_formatting():
    heading = Heading(
        level=1,
        children=[
            Text(value="Hello "),
            Strong(children=[Text(value="World")]),
            Emphasis(children=[Text(value="!")]),
        ],
    )
    assert heading_plain_text(heading.children) == "Hello World!"
