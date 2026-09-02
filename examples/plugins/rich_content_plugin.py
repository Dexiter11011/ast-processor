"""Rich content example plugin using the public semantic API."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Literal

from md2docx.plugin_api import (
    DirectiveDefinition,
    PluginMetadata,
    PluginRegistry,
)
from md2docx.semantic import (
    bold,
    fragment,
    hyperlink,
    italic,
    line_break,
    paragraph,
    text,
)
from md2docx.styles.definition import ParagraphStyle, RunStyle, StyleDefinition

PLUGIN_NAME = "example.rich"
AST_TYPE = f"{PLUGIN_NAME}.demo"
STYLE_ID = f"{PLUGIN_NAME}.demo"

RICH_DIRECTIVE = re.compile(
    r'^\s*<!--\s*rich:\s*(?P<label>.+?)\s*-->\s*$',
    re.IGNORECASE,
)


@dataclass
class RichDemo:
    label: str
    type: Literal["example.rich.demo"] = AST_TYPE
    children: list = field(default_factory=list)


class RichDemoHandler:
    def process(self, node: RichDemo, context: Any, processor: Any):
        del context, processor
        return fragment(
            paragraph(
                STYLE_ID,
                bold(text("Rich: ")),
                italic(text(node.label)),
                line_break(),
                hyperlink("https://example.com", text("Example link")),
            )
        )


class RichPlugin:
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=PLUGIN_NAME,
            version="1.0.0",
            description="Demonstrates rich semantic composition for plugins.",
        )

    def register(self, registry: PluginRegistry) -> None:
        registry.register_handler(AST_TYPE, RichDemoHandler())
        registry.register_style(
            StyleDefinition(
                semantic_id=STYLE_ID,
                ooxml_id="RichDemo",
                name="Rich Demo",
                paragraph=ParagraphStyle(spacing_after=120),
                run=RunStyle(bold=False),
            )
        )
        registry.register_directive(
            DirectiveDefinition(
                name=f"{PLUGIN_NAME}.directive",
                pattern=RICH_DIRECTIVE,
                to_ast=lambda match, _line: RichDemo(label=match.group("label").strip()),
            )
        )


plugin = RichPlugin()
