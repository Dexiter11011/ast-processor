"""Markdown parser producing md2docx AST."""

from __future__ import annotations

import re
from dataclasses import replace

from markdown_it import MarkdownIt
from mdit_py_plugins.deflist import deflist_plugin
from mdit_py_plugins.footnote import footnote_plugin

from md2docx.parser.block_directive import (
    match_caption_directive,
    match_field_directive,
    match_footer_directive,
    match_header_directive,
    match_lof_directive,
    match_lot_directive,
    match_page_break,
    match_ref_directive,
    match_section_break,
    match_toc_directive,
)
from md2docx.parser.caption_marker import CaptionMarker
from md2docx.parser.cell_markers import parse_cell_content
from md2docx.parser.html_adapter import (
    ALLOWED_TAGS,
    BLOCKED_TAGS,
    block_tag_name,
    parse_html_tag,
    validate_html_tag,
    wrap_html_close_tag,
)
from md2docx.parser.errors import HtmlParseError
from md2docx.parser.ref_marker import RefMarker
from md2docx.parser.table_directive import is_table_directive_text, parse_cell_align, parse_table_directive
from md2docx.ast.table_merge import apply_horizontal_merge, apply_vertical_merge

from md2docx.ast.types import (
    BlockNode,
    BlockQuote,
    CodeBlock,
    DefinitionItem,
    DefinitionList,
    Document,
    Emphasis,
    FootnoteDefinition,
    FootnoteReference,
    Heading,
    FooterDirective,
    FieldDirective,
    HeaderDirective,
    HorizontalRule,
    Image,
    InlineCode,
    InlineNode,
    LineBreak,
    Link,
    List,
    ListItem,
    ListOfFigures,
    ListOfTables,
    PageBreak,
    Paragraph,
    SectionBreak,
    Strikethrough,
    Strong,
    Table,
    TableOfContents,
    TableCell,
    TableRow,
    Text,
)


TASK_PREFIX = re.compile(r"^\[([ xX])\]\s+")


class MarkdownParser:
    """Parse Markdown source into a typed Document AST."""

    def __init__(self, plugin_registry=None) -> None:
        self._plugin_registry = plugin_registry
        self._md = (
            MarkdownIt("commonmark", {"html": True})
            .enable("table")
            .enable("strikethrough")
            .use(footnote_plugin, inline=True, move_to_end=True, always_match_refs=True)
            .use(deflist_plugin)
        )

    def parse(self, source: str, *, source_path: str | None = None) -> Document:
        if not source.strip():
            return Document(children=[])
        children: list[BlockNode] = []
        footnotes: list[FootnoteDefinition] = []
        buffer: list[str] = []
        line_no = 0
        for line in source.splitlines(keepends=True):
            line_no += 1
            stripped = line.strip()
            if match_page_break(stripped):
                if buffer:
                    chunk_blocks, chunk_footnotes = self._parse_markdown_chunk(
                        "".join(buffer), source_path=source_path
                    )
                    children.extend(chunk_blocks)
                    footnotes.extend(chunk_footnotes)
                    buffer = []
                children.append(PageBreak())
                continue
            layout_spec = match_section_break(stripped)
            if layout_spec is not None:
                if buffer:
                    chunk_blocks, chunk_footnotes = self._parse_markdown_chunk(
                        "".join(buffer), source_path=source_path
                    )
                    children.extend(chunk_blocks)
                    footnotes.extend(chunk_footnotes)
                    buffer = []
                children.append(SectionBreak(layout_spec=layout_spec))
                continue
            header_text = match_header_directive(stripped)
            if header_text is not None:
                if buffer:
                    chunk_blocks, chunk_footnotes = self._parse_markdown_chunk(
                        "".join(buffer), source_path=source_path
                    )
                    children.extend(chunk_blocks)
                    footnotes.extend(chunk_footnotes)
                    buffer = []
                children.append(HeaderDirective(text=header_text))
                continue
            footer_text = match_footer_directive(stripped)
            if footer_text is not None:
                if buffer:
                    chunk_blocks, chunk_footnotes = self._parse_markdown_chunk(
                        "".join(buffer), source_path=source_path
                    )
                    children.extend(chunk_blocks)
                    footnotes.extend(chunk_footnotes)
                    buffer = []
                children.append(FooterDirective(text=footer_text))
                continue
            field_directive = match_field_directive(stripped)
            if field_directive is not None:
                if buffer:
                    chunk_blocks, chunk_footnotes = self._parse_markdown_chunk(
                        "".join(buffer), source_path=source_path
                    )
                    children.extend(chunk_blocks)
                    footnotes.extend(chunk_footnotes)
                    buffer = []
                kind, target = field_directive
                children.append(FieldDirective(kind=kind, target=target))
                continue
            toc_levels = match_toc_directive(stripped)
            if toc_levels is not None:
                if buffer:
                    chunk_blocks, chunk_footnotes = self._parse_markdown_chunk(
                        "".join(buffer), source_path=source_path
                    )
                    children.extend(chunk_blocks)
                    footnotes.extend(chunk_footnotes)
                    buffer = []
                min_level, max_level = toc_levels
                children.append(TableOfContents(min_level=min_level, max_level=max_level))
                continue
            if match_lof_directive(stripped):
                if buffer:
                    chunk_blocks, chunk_footnotes = self._parse_markdown_chunk(
                        "".join(buffer), source_path=source_path
                    )
                    children.extend(chunk_blocks)
                    footnotes.extend(chunk_footnotes)
                    buffer = []
                children.append(ListOfFigures())
                continue
            if match_lot_directive(stripped):
                if buffer:
                    chunk_blocks, chunk_footnotes = self._parse_markdown_chunk(
                        "".join(buffer), source_path=source_path
                    )
                    children.extend(chunk_blocks)
                    footnotes.extend(chunk_footnotes)
                    buffer = []
                children.append(ListOfTables())
                continue
            caption_directive = match_caption_directive(stripped)
            if caption_directive is not None:
                if buffer:
                    chunk_blocks, chunk_footnotes = self._parse_markdown_chunk(
                        "".join(buffer), source_path=source_path
                    )
                    children.extend(chunk_blocks)
                    footnotes.extend(chunk_footnotes)
                    buffer = []
                kind, text = caption_directive
                children.append(CaptionMarker(kind=kind, text=text, line=line_no))
                continue
            ref_directive = match_ref_directive(stripped)
            if ref_directive is not None:
                if buffer:
                    chunk_blocks, chunk_footnotes = self._parse_markdown_chunk(
                        "".join(buffer), source_path=source_path
                    )
                    children.extend(chunk_blocks)
                    footnotes.extend(chunk_footnotes)
                    buffer = []
                kind, slug, prefix = ref_directive
                children.append(RefMarker(kind=kind, slug=slug, prefix=prefix, line=line_no))
                continue
            if self._plugin_registry is not None:
                plugin_node = self._plugin_registry.match_directive(stripped, line_no=line_no)
                if plugin_node is not None:
                    if buffer:
                        chunk_blocks, chunk_footnotes = self._parse_markdown_chunk(
                            "".join(buffer), source_path=source_path
                        )
                        children.extend(chunk_blocks)
                        footnotes.extend(chunk_footnotes)
                        buffer = []
                    children.append(plugin_node)
                    continue
            buffer.append(line)
        if buffer:
            chunk_blocks, chunk_footnotes = self._parse_markdown_chunk("".join(buffer), source_path=source_path)
            children.extend(chunk_blocks)
            footnotes.extend(chunk_footnotes)
        return Document(children=children, footnotes=footnotes)

    def _parse_markdown_chunk(
        self,
        source: str,
        *,
        source_path: str | None = None,
    ) -> tuple[list[BlockNode], list[FootnoteDefinition]]:
        if not source.strip():
            return [], []
        tokens = self._md.parse(source)
        footnotes: list[FootnoteDefinition] = []
        blocks = self._convert_blocks(tokens, source, footnotes, source_path=source_path)
        return blocks, footnotes

    def _convert_blocks(
        self,
        tokens,
        source: str,
        footnotes: list[FootnoteDefinition],
        *,
        source_path: str | None = None,
    ) -> list[BlockNode]:
        blocks: list[BlockNode] = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.type == "paragraph_open":
                inline_tokens, i = self._collect_until(tokens, i + 1, "paragraph_close")
                if _is_single_image_paragraph(inline_tokens):
                    image_token = _single_image_token(inline_tokens)
                    blocks.append(
                        Image(
                            src=str(image_token.attrGet("src") or ""),
                            alt=image_token.content or "",
                        )
                    )
                elif not _is_table_directive_paragraph(inline_tokens, source):
                    blocks.append(
                        Paragraph(
                            children=self._convert_inlines(
                                inline_tokens,
                                source,
                                source_path=source_path,
                                line=_token_line(token),
                            )
                        )
                    )
            elif token.type == "heading_open":
                level = int(token.tag[1])
                inline_tokens, i = self._collect_until(tokens, i + 1, "heading_close")
                blocks.append(
                    Heading(
                        level=level,
                        children=self._convert_inlines(
                            inline_tokens,
                            source,
                            source_path=source_path,
                            line=_token_line(token),
                        ),
                    )
                )
            elif token.type == "bullet_list_open":
                items, i = self._convert_list(
                    tokens, i, ordered=False, source=source, footnotes=footnotes, source_path=source_path
                )
                blocks.append(List(ordered=False, items=_apply_task_list_metadata(items)))
            elif token.type == "ordered_list_open":
                items, i = self._convert_list(
                    tokens, i, ordered=True, source=source, footnotes=footnotes, source_path=source_path
                )
                blocks.append(List(ordered=True, items=_apply_task_list_metadata(items)))
            elif token.type == "blockquote_open":
                inner, i = self._collect_blocks_until(
                    tokens, i + 1, "blockquote_close", source, footnotes, source_path=source_path
                )
                blocks.append(BlockQuote(children=inner))
            elif token.type == "fence":
                blocks.append(CodeBlock(value=token.content, language=token.info or ""))
                i += 1
            elif token.type == "hr":
                blocks.append(HorizontalRule())
                i += 1
            elif token.type == "table_open":
                table, i = self._convert_table(tokens, i, source, token.map[0] if token.map else None, source_path)
                blocks.append(table)
            elif token.type == "dl_open":
                definition_list, i = self._convert_definition_list(
                    tokens, i, source, footnotes, source_path=source_path
                )
                blocks.append(definition_list)
            elif token.type == "footnote_block_open":
                footnotes.extend(
                    self._convert_footnote_block(tokens, i, source, footnotes, source_path=source_path)
                )
                while i < len(tokens) and tokens[i].type != "footnote_block_close":
                    i += 1
                i += 1
            elif token.type == "html_block":
                content = (token.content or "").strip()
                if content.startswith("<!--"):
                    i += 1
                    continue
                tag_name = block_tag_name(token.content) or "html"
                raise HtmlParseError(
                    f"unsupported HTML element: {tag_name}",
                    path=source_path,
                    line=_token_line(token),
                )
            else:
                i += 1
        return blocks

    def _convert_footnote_block(
        self,
        tokens,
        start: int,
        source: str,
        footnotes: list[FootnoteDefinition],
        *,
        source_path: str | None = None,
    ) -> list[FootnoteDefinition]:
        definitions: list[FootnoteDefinition] = []
        seen_labels: set[str] = set()
        i = start + 1
        while i < len(tokens) and tokens[i].type != "footnote_block_close":
            if tokens[i].type == "footnote_open":
                label = str(tokens[i].meta.get("label", ""))
                if label in seen_labels:
                    from md2docx.parser.errors import FootnoteParseError

                    raise FootnoteParseError(
                        f"duplicate footnote definition: {label}",
                        path=source_path,
                    )
                seen_labels.add(label)
                inner_tokens: list = []
                i += 1
                while i < len(tokens) and tokens[i].type != "footnote_close":
                    if tokens[i].type != "footnote_anchor":
                        inner_tokens.append(tokens[i])
                    i += 1
                inner_blocks = self._convert_blocks(
                    inner_tokens,
                    source,
                    footnotes,
                    source_path=source_path,
                )
                definitions.append(FootnoteDefinition(label=label, children=inner_blocks))
            i += 1
        return definitions

    def _convert_definition_list(
        self,
        tokens,
        start: int,
        source: str,
        footnotes: list[FootnoteDefinition],
        *,
        source_path: str | None = None,
    ) -> tuple[DefinitionList, int]:
        items: list[DefinitionItem] = []
        current_terms: list[list[InlineNode]] = []
        i = start + 1
        while i < len(tokens) and tokens[i].type != "dl_close":
            if tokens[i].type == "dt_open":
                inline_tokens, i = self._collect_until(tokens, i + 1, "dt_close")
                current_terms.append(
                    self._convert_inlines(
                        inline_tokens,
                        source,
                        source_path=source_path,
                        line=_token_line(tokens[i - 1]),
                    )
                )
            elif tokens[i].type == "dd_open":
                inner, i = self._collect_blocks_until(
                    tokens, i + 1, "dd_close", source, footnotes, source_path=source_path
                )
                if not current_terms:
                    current_terms.append([])
                for term in current_terms:
                    items.append(DefinitionItem(term=term, description=inner))
                current_terms = []
            else:
                i += 1
        return DefinitionList(items=items), i + 1

    def _collect_blocks_until(
        self,
        tokens,
        start: int,
        close_type: str,
        source: str,
        footnotes: list[FootnoteDefinition],
        *,
        source_path: str | None = None,
    ) -> tuple[list[BlockNode], int]:
        inner_tokens = []
        depth = 1
        i = start
        while i < len(tokens):
            if tokens[i].type.endswith("_open") and tokens[i].type.replace("_open", "_close") == close_type:
                depth += 1
            elif tokens[i].type == close_type:
                depth -= 1
                if depth == 0:
                    return (
                        self._convert_blocks(
                            inner_tokens,
                            source,
                            footnotes,
                            source_path=source_path,
                        ),
                        i + 1,
                    )
            inner_tokens.append(tokens[i])
            i += 1
        return (
            self._convert_blocks(inner_tokens, source, footnotes, source_path=source_path),
            i,
        )

    def _convert_list(
        self,
        tokens,
        start: int,
        *,
        ordered: bool,
        source: str,
        footnotes: list[FootnoteDefinition],
        source_path: str | None = None,
    ) -> tuple[list[ListItem], int]:
        close = "ordered_list_close" if ordered else "bullet_list_close"
        items: list[ListItem] = []
        i = start + 1
        while i < len(tokens) and tokens[i].type != close:
            if tokens[i].type == "list_item_open":
                inner, i = self._collect_blocks_until(
                    tokens,
                    i + 1,
                    "list_item_close",
                    source,
                    footnotes,
                    source_path=source_path,
                )
                items.append(ListItem(children=inner))
            else:
                i += 1
        return items, i + 1

    def _convert_table(
        self,
        tokens,
        start: int,
        source: str,
        line_no: int | None,
        source_path: str | None = None,
    ) -> tuple[Table, int]:
        rows: list[TableRow] = []
        column_aligns: list[str] = []
        in_header = False
        directive = parse_table_directive(source, line_no)
        borders = directive.get("borders", "single")
        if borders not in {"single", "none", "double"}:
            borders = "single"
        i = start + 1
        while i < len(tokens) and tokens[i].type != "table_close":
            if tokens[i].type == "thead_open":
                in_header = True
                i += 1
                continue
            if tokens[i].type == "tbody_open":
                in_header = False
                i += 1
                continue
            if tokens[i].type in ("thead_close", "tbody_close"):
                i += 1
                continue
            if tokens[i].type == "tr_open":
                cells: list[TableCell] = []
                row_aligns: list[str] = []
                header_row = in_header
                i += 1
                while i < len(tokens) and tokens[i].type != "tr_close":
                    if tokens[i].type in ("th_open", "td_open"):
                        if tokens[i].type == "th_open":
                            header_row = True
                        close_type = tokens[i].type.replace("_open", "_close")
                        column_align = parse_cell_align(tokens[i].attrs)
                        inline_tokens, i = self._collect_until(tokens, i + 1, close_type)
                        row_aligns.append(column_align)
                        cells.append(
                            self._build_table_cell(
                                inline_tokens,
                                source,
                                column_align,
                                source_path=source_path,
                            )
                        )
                    else:
                        i += 1
                cells = apply_horizontal_merge(cells)
                if not column_aligns:
                    column_aligns = row_aligns
                rows.append(TableRow(cells=cells, header=header_row))
                i += 1
            else:
                i += 1
        rows = apply_vertical_merge(rows)
        return Table(rows=rows, column_aligns=column_aligns, borders=borders), i + 1

    def _build_table_cell(
        self,
        inline_tokens,
        source: str,
        column_align: str,
        *,
        source_path: str | None = None,
    ) -> TableCell:
        plain_text = _inline_tokens_plain_text(inline_tokens)
        parsed = parse_cell_content(plain_text)
        if parsed.vmerge_continue:
            return TableCell(vmerge_continue=True)
        align = parsed.align or column_align
        if parsed.text and parsed.text != plain_text:
            children = [
                Paragraph(
                    children=self._parse_inline_text(parsed.text, source, source_path=source_path)
                )
            ]
        elif parsed.text:
            children = [
                Paragraph(
                    children=self._convert_inlines(
                        inline_tokens,
                        source,
                        source_path=source_path,
                    )
                )
            ]
        else:
            children = []
        return TableCell(align=align, bg=parsed.bg, valign=parsed.valign, children=children)

    def _parse_inline_text(
        self,
        text: str,
        source: str,
        *,
        source_path: str | None = None,
    ) -> list[InlineNode]:
        tokens = self._md.parseInline(text, {})
        return self._convert_inlines(tokens, source, source_path=source_path)

    def _collect_until(self, tokens, start: int, close_type: str) -> tuple[list, int]:
        collected = []
        i = start
        while i < len(tokens):
            if tokens[i].type == close_type:
                return collected, i + 1
            collected.append(tokens[i])
            i += 1
        return collected, i

    def _convert_inlines(
        self,
        tokens,
        source: str,
        *,
        source_path: str | None = None,
        line: int | None = None,
    ) -> list[InlineNode]:
        output: list[InlineNode] = []
        stack: list[list[InlineNode]] = [output]
        open_tags: list[tuple[str, dict[str, str]]] = []
        flat_tokens = _flatten_inline_tokens(tokens)
        i = 0
        while i < len(flat_tokens):
            token = flat_tokens[i]
            token_line = _token_line(token) or line
            if token.type == "text":
                if token.content:
                    stack[-1].append(Text(value=token.content))
                i += 1
            elif token.type == "code_inline":
                stack[-1].append(InlineCode(value=token.content))
                i += 1
            elif token.type == "strong_open":
                inner, i = self._collect_until(flat_tokens, i + 1, "strong_close")
                stack[-1].append(Strong(children=self._convert_inlines(inner, source, source_path=source_path)))
            elif token.type == "em_open":
                inner, i = self._collect_until(flat_tokens, i + 1, "em_close")
                stack[-1].append(Emphasis(children=self._convert_inlines(inner, source, source_path=source_path)))
            elif token.type == "s_open":
                inner, i = self._collect_until(flat_tokens, i + 1, "s_close")
                stack[-1].append(Strikethrough(children=self._convert_inlines(inner, source, source_path=source_path)))
            elif token.type == "link_open":
                href = token.attrGet("href") or ""
                title = token.attrGet("title") or None
                inner, i = self._collect_until(flat_tokens, i + 1, "link_close")
                stack[-1].append(
                    Link(url=href, title=title, children=self._convert_inlines(inner, source, source_path=source_path))
                )
            elif token.type == "hardbreak":
                stack[-1].append(LineBreak())
                i += 1
            elif token.type == "softbreak":
                stack[-1].append(Text(value="\n"))
                i += 1
            elif token.type == "footnote_ref":
                label = str(token.meta.get("label", ""))
                stack[-1].append(FootnoteReference(label=label))
                i += 1
            elif token.type == "html_inline":
                html_tag = parse_html_tag(token.content)
                if html_tag is None or html_tag.name not in ALLOWED_TAGS:
                    if html_tag is not None and html_tag.name in BLOCKED_TAGS:
                        raise HtmlParseError(
                            f"unsupported HTML element: {html_tag.name}",
                            path=source_path,
                            line=token_line,
                        )
                    stack[-1].append(Text(value=token.content))
                    i += 1
                    continue
                html_tag = validate_html_tag(token.content, path=source_path, line=token_line)
                if html_tag.name == "br" and not html_tag.closing:
                    stack[-1].append(LineBreak())
                    i += 1
                    continue
                if html_tag.closing:
                    if not open_tags:
                        raise HtmlParseError(
                            f"unexpected closing HTML tag: {html_tag.name}",
                            path=source_path,
                            line=token_line,
                        )
                    tag_name, attrs = open_tags.pop()
                    if tag_name != html_tag.name:
                        raise HtmlParseError(
                            f"mismatched HTML tags: expected </{tag_name}>, got </{html_tag.name}>",
                            path=source_path,
                            line=token_line,
                        )
                    children = stack.pop()
                    stack[-1].append(wrap_html_close_tag(tag_name, attrs, children))
                    i += 1
                    continue
                open_tags.append((html_tag.name, html_tag.attrs))
                stack.append([])
                i += 1
            else:
                i += 1

        if open_tags:
            names = ", ".join(name for name, _ in open_tags)
            raise HtmlParseError(f"unclosed HTML tags: {names}", path=source_path, line=line)
        return output


def _token_line(token) -> int | None:
    if token.map:
        return token.map[0] + 1
    return None


def _flatten_inline_tokens(tokens) -> list:
    children = []
    for token in tokens:
        if token.type == "inline":
            children.extend(token.children or [])
        else:
            children.append(token)
    return children


def _inline_tokens_plain_text(tokens) -> str:
    parts: list[str] = []
    for token in _flatten_inline_tokens(tokens):
        if token.type == "text":
            parts.append(token.content)
        elif token.type == "code_inline":
            parts.append(token.content)
        elif token.type == "softbreak" or token.type == "hardbreak":
            parts.append("\n")
    return "".join(parts)


def _is_table_directive_paragraph(tokens, source: str) -> bool:
    children = _flatten_inline_tokens(tokens)
    if len(children) != 1 or children[0].type != "text":
        return False
    return is_table_directive_text(children[0].content)


def _is_single_image_paragraph(tokens) -> bool:
    children = _flatten_inline_tokens(tokens)
    return len(children) == 1 and children[0].type == "image"


def _single_image_token(tokens):
    return _flatten_inline_tokens(tokens)[0]


def _apply_task_list_metadata(items: list[ListItem]) -> list[ListItem]:
    result: list[ListItem] = []
    for item in items:
        detected = _detect_task_item(item)
        new_children: list = []
        for child in detected.children:
            if isinstance(child, List):
                new_children.append(replace(child, items=_apply_task_list_metadata(child.items)))
            else:
                new_children.append(child)
        result.append(replace(detected, children=new_children))
    return result


def _detect_task_item(item: ListItem) -> ListItem:
    if not item.children or item.children[0].type != "paragraph":
        return item
    para = item.children[0]
    if not para.children or para.children[0].type != "text":
        return item
    first = para.children[0]
    match = TASK_PREFIX.match(first.value)
    if not match:
        return item
    checked = match.group(1).lower() == "x"
    remainder = first.value[match.end() :]
    new_para_children: list[InlineNode] = []
    if remainder:
        new_para_children.append(Text(value=remainder))
    new_para_children.extend(para.children[1:])
    new_para = Paragraph(children=new_para_children)
    return ListItem(checked=checked, children=[new_para, *item.children[1:]])
