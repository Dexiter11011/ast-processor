"""Document-level bookmark registration and resolution."""

from __future__ import annotations

from dataclasses import dataclass, field

from md2docx.ast.types import Document, Heading
from md2docx.references.bookmark import Bookmark
from md2docx.references.slug import disambiguate_slug, heading_plain_text, slugify


@dataclass
class BookmarkManager:
    """Allocate bookmark IDs, register heading anchors, resolve internal links."""

    _next_id: int = 0
    _by_name: dict[str, Bookmark] = field(default_factory=dict)
    _heading_queue: list[Bookmark] = field(default_factory=list)
    _broken_targets: set[str] = field(default_factory=set)
    _heading_index: int = 0

    def allocate_id(self) -> int:
        bookmark_id = self._next_id
        self._next_id += 1
        return bookmark_id

    def register(self, name: str, *, bookmark_id: int | None = None) -> Bookmark:
        if name in self._by_name:
            return self._by_name[name]
        assigned_id = bookmark_id if bookmark_id is not None else self.allocate_id()
        bookmark = Bookmark(name=name, id=assigned_id)
        self._by_name[name] = bookmark
        return bookmark

    def resolve(self, name: str) -> Bookmark | None:
        return self._by_name.get(name)

    def register_headings(self, document: Document, navigation=None) -> None:
        """Pre-scan document headings and assign deterministic bookmark names."""
        slug_counts: dict[str, int] = {}
        self._heading_queue.clear()
        self._heading_index = 0
        self._walk_headings(document.children, slug_counts, navigation)

    def _walk_headings(self, nodes, slug_counts: dict[str, int], navigation) -> None:
        for node in nodes:
            if isinstance(node, Heading):
                plain = heading_plain_text(node.children)
                base = slugify(plain)
                name = disambiguate_slug(base, slug_counts)
                bookmark_id = self.allocate_id()
                bookmark = self.register(name, bookmark_id=bookmark_id)
                self._heading_queue.append(bookmark)
                if navigation is not None:
                    navigation.register_heading(
                        bookmark_name=name,
                        label=plain,
                        level=node.level,
                    )
            elif hasattr(node, "children"):
                children = getattr(node, "children", None)
                if isinstance(children, list):
                    self._walk_headings(children, slug_counts, navigation)
            elif hasattr(node, "items"):
                for item in node.items:
                    if hasattr(item, "description"):
                        self._walk_headings(item.description, slug_counts, navigation)
                    else:
                        self._walk_headings(getattr(item, "children", []), slug_counts, navigation)
            elif hasattr(node, "rows"):
                for row in node.rows:
                    for cell in row.cells:
                        self._walk_headings(cell.children, slug_counts, navigation)

    def next_heading_bookmark(self) -> Bookmark | None:
        """Return the next pre-registered heading bookmark in document order."""
        if self._heading_index >= len(self._heading_queue):
            return None
        bookmark = self._heading_queue[self._heading_index]
        self._heading_index += 1
        return bookmark

    def record_broken_target(self, name: str) -> None:
        self._broken_targets.add(name)

    @property
    def broken_targets(self) -> frozenset[str]:
        return frozenset(self._broken_targets)
