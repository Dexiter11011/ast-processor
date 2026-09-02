"""BookmarkManager unit tests."""

from md2docx.ast.types import Document, Heading, Text
from md2docx.references.manager import BookmarkManager


def test_register_headings_assigns_unique_slugs():
    doc = Document(
        children=[
            Heading(level=1, children=[Text(value="Introduction")]),
            Heading(level=1, children=[Text(value="Introduction")]),
            Heading(level=2, children=[Text(value="Details")]),
        ]
    )
    manager = BookmarkManager()
    manager.register_headings(doc)
    names = [b.name for b in manager._heading_queue]
    assert names == ["introduction", "introduction-1", "details"]


def test_resolve_registered_bookmark():
    manager = BookmarkManager()
    bookmark = manager.register("intro", bookmark_id=0)
    assert manager.resolve("intro") == bookmark
    assert manager.resolve("missing") is None
