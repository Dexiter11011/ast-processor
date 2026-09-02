"""AST node types for md2docx."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Union

from md2docx.ast.metadata import DocumentMetadata

# Block-level nodes (expanded in later iterations)
BlockNode = Union[
    "Paragraph",
    "Heading",
    "List",
    "BlockQuote",
    "CodeBlock",
    "HorizontalRule",
    "Image",
    "Table",
    "PageBreak",
    "SectionBreak",
    "HeaderDirective",
    "FooterDirective",
    "FieldDirective",
    "TableOfContents",
    "ListOfFigures",
    "ListOfFigures",
    "ListOfTables",
    "DefinitionList",
]

# Inline-level nodes (expanded in later iterations)
InlineNode = Union[
    "Text",
    "Strong",
    "Emphasis",
    "Strikethrough",
    "Link",
    "InlineCode",
    "LineBreak",
    "FootnoteReference",
]

AstNode = Union[BlockNode, InlineNode, "Document", "ListItem", "TableRow", "TableCell"]


@dataclass
class Document:
    type: Literal["document"] = "document"
    children: list[BlockNode] = field(default_factory=list)
    metadata: DocumentMetadata | None = None
    footnotes: list["FootnoteDefinition"] = field(default_factory=list)


@dataclass
class Paragraph:
    type: Literal["paragraph"] = "paragraph"
    children: list[InlineNode] = field(default_factory=list)


@dataclass
class Heading:
    type: Literal["heading"] = "heading"
    level: int = 1
    children: list[InlineNode] = field(default_factory=list)


@dataclass
class Text:
    type: Literal["text"] = "text"
    value: str = ""


@dataclass
class Strong:
    type: Literal["strong"] = "strong"
    children: list[InlineNode] = field(default_factory=list)


@dataclass
class Emphasis:
    type: Literal["emphasis"] = "emphasis"
    children: list[InlineNode] = field(default_factory=list)


@dataclass
class Strikethrough:
    type: Literal["strikethrough"] = "strikethrough"
    children: list[InlineNode] = field(default_factory=list)


@dataclass
class LineBreak:
    type: Literal["line_break"] = "line_break"


@dataclass
class FootnoteReference:
    type: Literal["footnote_reference"] = "footnote_reference"
    label: str = ""


@dataclass
class FootnoteDefinition:
    type: Literal["footnote_definition"] = "footnote_definition"
    label: str = ""
    children: list[BlockNode] = field(default_factory=list)


@dataclass
class DefinitionList:
    type: Literal["definition_list"] = "definition_list"
    items: list["DefinitionItem"] = field(default_factory=list)


@dataclass
class DefinitionItem:
    type: Literal["definition_item"] = "definition_item"
    term: list[InlineNode] = field(default_factory=list)
    description: list[BlockNode] = field(default_factory=list)


@dataclass
class Link:
    type: Literal["link"] = "link"
    url: str = ""
    title: str | None = None
    children: list[InlineNode] = field(default_factory=list)

    @property
    def is_internal(self) -> bool:
        return self.url.startswith("#")

    @property
    def bookmark_name(self) -> str:
        """Normalized bookmark name for internal links (without leading #)."""
        return self.url[1:].strip().casefold() if self.is_internal else ""


@dataclass
class InlineCode:
    type: Literal["inline_code"] = "inline_code"
    value: str = ""


@dataclass
class List:
    type: Literal["list"] = "list"
    ordered: bool = False
    items: list[ListItem] = field(default_factory=list)


@dataclass
class ListItem:
    type: Literal["list_item"] = "list_item"
    children: list[BlockNode] = field(default_factory=list)
    checked: bool | None = None


@dataclass
class BlockQuote:
    type: Literal["blockquote"] = "blockquote"
    children: list[BlockNode] = field(default_factory=list)


@dataclass
class CodeBlock:
    type: Literal["code_block"] = "code_block"
    value: str = ""
    language: str = ""


@dataclass
class HorizontalRule:
    type: Literal["horizontal_rule"] = "horizontal_rule"


@dataclass
class PageBreak:
    type: Literal["page_break"] = "page_break"


@dataclass
class SectionBreak:
    type: Literal["section_break"] = "section_break"
    layout_spec: str = "a4"


@dataclass
class HeaderDirective:
    type: Literal["header_directive"] = "header_directive"
    text: str = ""


@dataclass
class FooterDirective:
    type: Literal["footer_directive"] = "footer_directive"
    text: str = ""


@dataclass
class FieldDirective:
    type: Literal["field_directive"] = "field_directive"
    kind: str = ""
    target: str = ""


@dataclass
class TableOfContents:
    type: Literal["table_of_contents"] = "table_of_contents"
    min_level: int = 1
    max_level: int = 3


@dataclass
class ListOfFigures:
    type: Literal["list_of_figures"] = "list_of_figures"


@dataclass
class ListOfTables:
    type: Literal["list_of_tables"] = "list_of_tables"


@dataclass
class Image:
    type: Literal["image"] = "image"
    src: str = ""
    alt: str = ""


@dataclass
class Table:
    type: Literal["table"] = "table"
    rows: list[TableRow] = field(default_factory=list)
    column_aligns: list[str] = field(default_factory=list)
    borders: str = "single"


@dataclass
class TableRow:
    type: Literal["table_row"] = "table_row"
    cells: list[TableCell] = field(default_factory=list)
    header: bool = False


@dataclass
class TableCell:
    type: Literal["table_cell"] = "table_cell"
    children: list[BlockNode] = field(default_factory=list)
    align: str = ""
    bg: str = ""
    valign: str = ""
    colspan: int = 1
    rowspan: int = 1
    merged: bool = False
    vmerge_continue: bool = False
