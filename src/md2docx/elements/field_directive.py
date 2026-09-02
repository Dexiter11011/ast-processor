"""Body field directive handler."""

from __future__ import annotations

from md2docx.ast.types import FieldDirective
from md2docx.fields.errors import FieldError
from md2docx.ooxml import api
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext

_FIELD_LABELS = {
    "date": "DATE: ",
    "ref": "REF: ",
    "seq": "SEQ: ",
}


class FieldDirectiveHandler:
    """Insert a dynamic Word field paragraph in the document body."""

    def process(self, node: FieldDirective, context: ProcessingContext, processor: AstProcessor) -> None:
        style_id = context.styles.resolve("normal")
        kind = node.kind.strip().lower()
        label = _FIELD_LABELS.get(kind)
        if label is None:
            raise FieldError(f"unsupported field directive kind: {node.kind!r}")

        if kind == "date":
            field_runs = [context.fields.date_field()]
        elif kind == "ref":
            if not node.target:
                raise FieldError("field directive ref requires a bookmark name")
            field_runs = context.fields.ref_field(node.target, bookmarks=context.bookmarks)
        elif kind == "seq":
            if not node.target:
                raise FieldError("field directive seq requires a sequence name")
            field_runs = context.fields.seq_field(node.target)
        else:
            raise FieldError(f"unsupported field directive kind: {node.kind!r}")

        paragraph = api.paragraph([api.run(label), *field_runs], style_id=style_id)
        context.document.add_body_element(paragraph)
