"""Example notes plugin for md2docx."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Literal

from md2docx.plugin_api import (
    DirectiveDefinition,
    PluginMetadata,
    PluginRegistry,
    TemplateRegionDefinition,
    ValidationPhase,
    ValidatorDefinition,
)
from md2docx.semantic import (
    bold,
    fragment,
    paragraph,
    text,
)
from md2docx.styles.definition import ParagraphStyle, RunStyle, StyleDefinition

PLUGIN_NAME = "example.notes"
AST_TYPE = f"{PLUGIN_NAME}.note"
STYLE_ID = f"{PLUGIN_NAME}.note"
REGION_NAME = "example_note"

NOTE_DIRECTIVE = re.compile(
    r'^\s*<!--\s*note:\s*(?P<text>.+?)\s*-->\s*$',
    re.IGNORECASE,
)


@dataclass
class CustomNote:
    """Plugin-defined block node for note directives."""

    text: str
    type: Literal["example.notes.note"] = AST_TYPE
    children: list = field(default_factory=list)


class CustomNoteHandler:
    """Render a note block as a styled paragraph."""

    def process(self, node: CustomNote, context: Any, processor: Any):
        if not node.text.strip():
            raise ValueError("note text must not be empty")
        return fragment(
            paragraph(
                STYLE_ID,
                bold(text("Note: ")),
                text(node.text),
            )
        )


def _render_template_region(context: Any):
    sem = SemanticContext.from_processing_context(context)
    return fragment(
        paragraph(
            STYLE_ID,
            bold(text("Note: ")),
            text("Template region"),
        )
    )


def _validate_note_ast(document) -> None:
    for child in document.children:
        if getattr(child, "type", None) == AST_TYPE and not getattr(child, "text", "").strip():
            raise ValueError("CustomNote text must not be empty")


class NotesPlugin:
    """Canonical example plugin demonstrating the public extension API."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=PLUGIN_NAME,
            version="1.0.0",
            description="Adds note directives, styles, and template regions.",
        )

    def register(self, registry: PluginRegistry) -> None:
        registry.register_handler(AST_TYPE, CustomNoteHandler())
        registry.register_style(
            StyleDefinition(
                semantic_id=STYLE_ID,
                ooxml_id="ExampleNote",
                name="Example Note",
                paragraph=ParagraphStyle(spacing_before=120, spacing_after=120),
                run=RunStyle(bold=True, color="C00000"),
            )
        )
        registry.register_directive(
            DirectiveDefinition(
                name=f"{PLUGIN_NAME}.directive",
                pattern=NOTE_DIRECTIVE,
                to_ast=lambda match, _line: CustomNote(text=match.group("text").strip()),
            )
        )
        registry.register_template_region(
            TemplateRegionDefinition(
                placeholder_name=REGION_NAME,
                render_fragment=_render_template_region,
                strip_ast_types=frozenset({AST_TYPE}),
            )
        )
        registry.register_validator(
            ValidatorDefinition(
                name=f"{PLUGIN_NAME}.validate_notes",
                phase=ValidationPhase.SEMANTIC,
                validate=_validate_note_ast,
            )
        )


plugin = NotesPlugin()
