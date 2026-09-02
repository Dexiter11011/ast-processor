"""Resolve and validate logical references against navigation targets."""

from __future__ import annotations

from dataclasses import dataclass, field

from md2docx.captions.kinds import CaptionKind
from md2docx.fields.errors import MissingRefTargetError
from md2docx.navigation.errors import ReferenceKindMismatchError
from md2docx.navigation.kinds import NavigationTargetKind, caption_kind_to_navigation_kind
from md2docx.navigation.registry import NavigationRegistry
from md2docx.references.manager import BookmarkManager
from md2docx.references.reference import CrossReference


@dataclass
class ReferenceManager:
    """Resolve logical targets to bookmarks and validate typed cross-references."""

    navigation: NavigationRegistry
    bookmarks: BookmarkManager = field(default_factory=BookmarkManager)
    _pending: list[CrossReference] = field(default_factory=list)

    def resolve_bookmark_for_ref(
        self,
        target: str,
        kind: CaptionKind | None = None,
    ) -> str:
        """Return bookmark name for a REF field after validation."""
        bookmark = self.bookmarks.resolve(target)
        if bookmark is None:
            raise MissingRefTargetError(
                f'REF field target bookmark "{target}" was not found'
            )
        if kind is not None:
            nav_target = self.navigation.resolve_by_bookmark(target)
            expected = caption_kind_to_navigation_kind(kind)
            if nav_target is None:
                raise ReferenceKindMismatchError(
                    f'reference target "{target}" is not a registered navigation target'
                )
            if nav_target.kind is not expected:
                kind_label = expected.value
                raise ReferenceKindMismatchError(
                    f'reference target "{target}" is not a {kind_label} target'
                )
        return bookmark.name

    def resolve_link_anchor(self, anchor: str) -> str | None:
        """Resolve an internal hyperlink anchor; None if bookmark is missing."""
        bookmark = self.bookmarks.resolve(anchor)
        if bookmark is None:
            return None
        return bookmark.name

    def register_pending_ref(self, ref: CrossReference) -> None:
        self._pending.append(ref)

    def validate_pending_refs(self) -> None:
        for ref in self._pending:
            self.resolve_bookmark_for_ref(ref.target, ref.kind)

    def validate_cross_reference(self, ref: CrossReference) -> str:
        return self.resolve_bookmark_for_ref(ref.target, ref.kind)
