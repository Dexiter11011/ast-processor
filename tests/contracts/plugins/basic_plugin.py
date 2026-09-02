"""Canonical contract plugin using only public Tier A/B imports."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Literal

from md2docx.ooxml import api
from md2docx.plugin_api import (
    DirectiveDefinition,
    PluginMetadata,
    PluginRegistry,
    TemplateRegionDefinition,
    ValidationPhase,
    ValidatorDefinition,
)
from md2docx.styles.definition import ParagraphStyle, RunStyle, StyleDefinition

PLUGIN_NAME = "contract.basic"
AST_TYPE = f"{PLUGIN_NAME}.callout"
STYLE_ID = f"{PLUGIN_NAME}.callout"
REGION_NAME = "contract_callout"

CALLOUT_DIRECTIVE = re.compile(
    r'^\s*<!--\s*callout:\s*(?P<text>.+?)\s*-->\s*$',
    re.IGNORECASE,
)


@dataclass
class CalloutNode:
    text: str
    type: Literal["contract.basic.callout"] = AST_TYPE
    children: list = field(default_factory=list)


class CalloutHandler:
    def process(self, node: CalloutNode, context: Any, processor: Any) -> None:
        style_id = context.styles.to_ooxml(STYLE_ID)
        paragraph = api.paragraph(
            [api.run(f"Callout: {node.text}")],
            style_id=style_id,
        )
        context.document.add_body_element(paragraph)


def _render_region(context: Any) -> list:
    style_id = context.styles.to_ooxml(STYLE_ID)
    return [
        api.paragraph(
            [api.run("Callout: Template region")],
            style_id=style_id,
        )
    ]


def _validate(document) -> None:
    for child in document.children:
        if getattr(child, "type", None) == AST_TYPE and not getattr(child, "text", "").strip():
            raise ValueError("callout text must not be empty")


class BasicPlugin:
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(name=PLUGIN_NAME, version="1.0.0")

    def register(self, registry: PluginRegistry) -> None:
        registry.register_handler(AST_TYPE, CalloutHandler())
        registry.register_style(
            StyleDefinition(
                semantic_id=STYLE_ID,
                ooxml_id="ContractCallout",
                name="Contract Callout",
                paragraph=ParagraphStyle(spacing_before=120, spacing_after=120),
                run=RunStyle(bold=True),
            )
        )
        registry.register_directive(
            DirectiveDefinition(
                name=f"{PLUGIN_NAME}.directive",
                pattern=CALLOUT_DIRECTIVE,
                to_ast=lambda match, _line: CalloutNode(text=match.group("text").strip()),
            )
        )
        registry.register_template_region(
            TemplateRegionDefinition(
                placeholder_name=REGION_NAME,
                render_fragment=_render_region,
                strip_ast_types=frozenset({AST_TYPE}),
            )
        )
        registry.register_validator(
            ValidatorDefinition(
                name=f"{PLUGIN_NAME}.validate",
                phase=ValidationPhase.SEMANTIC,
                validate=_validate,
            )
        )


plugin = BasicPlugin()
