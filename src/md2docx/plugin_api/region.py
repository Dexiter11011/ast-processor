"""Template region extension definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Union

from lxml import etree

if TYPE_CHECKING:
    from md2docx.processor.context import ProcessingContext
    from md2docx.semantic.fragment import RichDocumentFragment

FragmentRenderer = Callable[["ProcessingContext"], Union["RichDocumentFragment", list[etree._Element], None]]


@dataclass(frozen=True)
class TemplateRegionDefinition:
    """Plugin-defined template insertion region."""

    placeholder_name: str
    render_fragment: FragmentRenderer
    strip_ast_types: frozenset[str] = frozenset()
