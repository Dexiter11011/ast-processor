"""Element handlers registry factory."""

from md2docx.elements.blockquote import BlockQuoteHandler
from md2docx.elements.code_block import CodeBlockHandler
from md2docx.elements.emphasis import EmphasisHandler
from md2docx.elements.heading import HeadingHandler
from md2docx.elements.horizontal_rule import HorizontalRuleHandler
from md2docx.elements.image import ImageHandler
from md2docx.elements.inline_code import InlineCodeHandler
from md2docx.elements.link import LinkHandler
from md2docx.elements.line_break import LineBreakHandler
from md2docx.elements.list_of_figures import ListOfFiguresHandler
from md2docx.elements.list_of_tables import ListOfTablesHandler
from md2docx.elements.strikethrough import StrikethroughHandler
from md2docx.elements.list import ListHandler
from md2docx.elements.list_item import ListItemHandler
from md2docx.elements.cross_reference import CrossReferenceHandler
from md2docx.elements.definition_list import DefinitionListHandler
from md2docx.elements.figure import FigureHandler
from md2docx.elements.field_directive import FieldDirectiveHandler
from md2docx.elements.footnote_reference import FootnoteReferenceHandler
from md2docx.elements.footer_directive import FooterDirectiveHandler
from md2docx.elements.header_directive import HeaderDirectiveHandler
from md2docx.elements.section_break import SectionBreakHandler
from md2docx.elements.page_break import PageBreakHandler
from md2docx.elements.paragraph import ParagraphHandler
from md2docx.elements.strong import StrongHandler
from md2docx.elements.table import TableHandler
from md2docx.elements.table_cell import TableCellHandler
from md2docx.elements.table_row import TableRowHandler
from md2docx.elements.table_with_caption import TableWithCaptionHandler
from md2docx.elements.text import TextHandler
from md2docx.elements.toc import TableOfContentsHandler
from md2docx.processor.registry import HandlerRegistry


def create_default_registry() -> HandlerRegistry:
    """Wire all built-in Markdown element handlers into a registry."""
    return (
        HandlerRegistry()
        .register("paragraph", ParagraphHandler())
        .register("heading", HeadingHandler())
        .register("text", TextHandler())
        .register("strong", StrongHandler())
        .register("emphasis", EmphasisHandler())
        .register("strikethrough", StrikethroughHandler())
        .register("line_break", LineBreakHandler())
        .register("footnote_reference", FootnoteReferenceHandler())
        .register("inline_code", InlineCodeHandler())
        .register("link", LinkHandler())
        .register("list", ListHandler())
        .register("list_item", ListItemHandler())
        .register("blockquote", BlockQuoteHandler())
        .register("horizontal_rule", HorizontalRuleHandler())
        .register("page_break", PageBreakHandler())
        .register("section_break", SectionBreakHandler())
        .register("header_directive", HeaderDirectiveHandler())
        .register("footer_directive", FooterDirectiveHandler())
        .register("field_directive", FieldDirectiveHandler())
        .register("figure", FigureHandler())
        .register("table_with_caption", TableWithCaptionHandler())
        .register("cross_reference", CrossReferenceHandler())
        .register("table_of_contents", TableOfContentsHandler())
        .register("list_of_figures", ListOfFiguresHandler())
        .register("list_of_tables", ListOfTablesHandler())
        .register("code_block", CodeBlockHandler())
        .register("definition_list", DefinitionListHandler())
        .register("image", ImageHandler())
        .register("table", TableHandler())
        .register("table_row", TableRowHandler())
        .register("table_cell", TableCellHandler())
    )
