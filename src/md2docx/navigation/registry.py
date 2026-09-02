"""Document-order registry of semantic navigation targets."""

from __future__ import annotations

from dataclasses import dataclass, field

from md2docx.navigation.kinds import NavigationTargetKind
from md2docx.navigation.target import NavigationTarget


@dataclass
class NavigationRegistry:
    """Track heading, figure, and table navigation targets in document order."""

    _targets: list[NavigationTarget] = field(default_factory=list)
    _by_bookmark: dict[str, NavigationTarget] = field(default_factory=dict)

    def register(self, target: NavigationTarget) -> None:
        if target.bookmark_name in self._by_bookmark:
            return
        self._targets.append(target)
        self._by_bookmark[target.bookmark_name] = target

    def register_heading(
        self,
        *,
        bookmark_name: str,
        label: str,
        level: int,
    ) -> NavigationTarget:
        target = NavigationTarget(
            kind=NavigationTargetKind.HEADING,
            name=bookmark_name,
            bookmark_name=bookmark_name,
            label=label,
            level=level,
        )
        self.register(target)
        return target

    def register_figure(
        self,
        *,
        bookmark_name: str,
        label: str,
    ) -> NavigationTarget:
        logical_name = _logical_caption_name(bookmark_name, prefix="figure-")
        target = NavigationTarget(
            kind=NavigationTargetKind.FIGURE,
            name=logical_name,
            bookmark_name=bookmark_name,
            label=label,
        )
        self.register(target)
        return target

    def register_table(
        self,
        *,
        bookmark_name: str,
        label: str,
    ) -> NavigationTarget:
        logical_name = _logical_caption_name(bookmark_name, prefix="table-")
        target = NavigationTarget(
            kind=NavigationTargetKind.TABLE,
            name=logical_name,
            bookmark_name=bookmark_name,
            label=label,
        )
        self.register(target)
        return target

    def resolve_by_bookmark(self, bookmark_name: str) -> NavigationTarget | None:
        return self._by_bookmark.get(bookmark_name)

    def targets_of_kind(self, kind: NavigationTargetKind) -> list[NavigationTarget]:
        return [target for target in self._targets if target.kind is kind]

    @property
    def targets(self) -> tuple[NavigationTarget, ...]:
        return tuple(self._targets)

    @property
    def bookmark_names(self) -> frozenset[str]:
        return frozenset(self._by_bookmark)


def _logical_caption_name(bookmark_name: str, *, prefix: str) -> str:
    if bookmark_name.startswith(prefix):
        return bookmark_name[len(prefix) :]
    return bookmark_name
