"""Cross-reference block element handler."""

from __future__ import annotations

from md2docx.captions.model import CrossReferenceBlock
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext


class CrossReferenceHandler:
    """Convert a CrossReferenceBlock into a REF field paragraph."""

    def process(self, node: CrossReferenceBlock, context: ProcessingContext, processor: AstProcessor) -> None:
        del processor
        context.captions.render_cross_reference(node.reference, context)
