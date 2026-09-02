"""Coalesce parser markers into semantic caption/navigation AST nodes."""

from __future__ import annotations

from md2docx.ast.types import Document, Image, Table
from md2docx.captions.kinds import CaptionKind
from md2docx.captions.model import Caption, CrossReferenceBlock, Figure, TableWithCaption
from md2docx.parser.caption_marker import CaptionMarker
from md2docx.parser.errors import CaptionParseError
from md2docx.parser.ref_marker import RefMarker
from md2docx.references.reference import CrossReference


def apply_caption_transform(document: Document, *, source_path: str | None = None) -> Document:
    """Replace caption/ref markers with Figure, TableWithCaption, and CrossReferenceBlock nodes."""
    transformed: list = []
    i = 0
    children = document.children
    while i < len(children):
        node = children[i]

        if isinstance(node, RefMarker):
            transformed.append(_ref_marker_to_block(node))
            i += 1
            continue

        if isinstance(node, Image):
            if (
                i + 1 < len(children)
                and isinstance(children[i + 1], CaptionMarker)
                and children[i + 1].kind is CaptionKind.FIGURE
            ):
                marker = children[i + 1]
                transformed.append(
                    Figure(
                        image=node,
                        caption=Caption(kind=CaptionKind.FIGURE, text=marker.text),
                    )
                )
                i += 2
                continue
            transformed.append(node)
            i += 1
            continue

        if isinstance(node, CaptionMarker):
            if node.kind is CaptionKind.TABLE:
                if i + 1 < len(children) and isinstance(children[i + 1], Table):
                    transformed.append(
                        TableWithCaption(
                            caption=Caption(kind=CaptionKind.TABLE, text=node.text),
                            table=children[i + 1],
                        )
                    )
                    i += 2
                    continue
                raise CaptionParseError(
                    "table caption directive must be immediately followed by a table",
                    line=node.line,
                    path=source_path,
                )
            raise CaptionParseError(
                "figure caption directive must immediately follow an image",
                line=node.line,
                path=source_path,
            )

        transformed.append(node)
        i += 1

    return Document(children=transformed, metadata=document.metadata, footnotes=document.footnotes)


def _ref_marker_to_block(marker: RefMarker) -> CrossReferenceBlock:
    return CrossReferenceBlock(
        reference=CrossReference(
            target=normalize_ref_target(marker.kind, marker.slug),
            kind=marker.kind,
            prefix=marker.prefix,
        )
    )


def normalize_ref_target(kind: CaptionKind, slug: str) -> str:
    """Map a Markdown ref slug to the bookmark name used by CaptionService."""
    prefix = "figure" if kind is CaptionKind.FIGURE else "table"
    if slug.startswith(f"{prefix}-"):
        return slug
    return f"{prefix}-{slug}"
