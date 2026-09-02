"""Multi-region template composition plan."""

from __future__ import annotations

from dataclasses import dataclass, field

from lxml import etree

from md2docx.templates.placeholders import PlaceholderKind, TemplatePlaceholder


@dataclass(frozen=True)
class TemplateCompositionPlan:
    """Ordered fragment insertions derived from scanned template placeholders."""

    content_fragment: list[etree._Element]
    navigation_fragments: dict[str, list[etree._Element]] = field(default_factory=dict)
    plugin_fragments: dict[str, list[etree._Element]] = field(default_factory=dict)

    def fragment_for(self, placeholder: TemplatePlaceholder) -> list[etree._Element]:
        if placeholder.kind is PlaceholderKind.CONTENT:
            return self.content_fragment
        if placeholder.kind is PlaceholderKind.NAVIGATION:
            return self.navigation_fragments[placeholder.name]
        if placeholder.kind is PlaceholderKind.PLUGIN:
            return self.plugin_fragments[placeholder.name]
        raise ValueError(f"placeholder {placeholder.name!r} is not a fragment region")

    def fragment_placeholders(self, placeholders: list[TemplatePlaceholder]) -> list[TemplatePlaceholder]:
        return [
            item
            for item in placeholders
            if item.kind
            in (PlaceholderKind.CONTENT, PlaceholderKind.NAVIGATION, PlaceholderKind.PLUGIN)
        ]
