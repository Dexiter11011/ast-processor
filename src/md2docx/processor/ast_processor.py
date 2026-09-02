"""AST processor — walks AST and delegates to handlers."""

from __future__ import annotations

from md2docx.ast.types import AstNode, Document
from md2docx.processor.context import ProcessingContext
from md2docx.processor.registry import HandlerRegistry


class AstProcessor:
    """Process AST nodes via registered element handlers."""

    def __init__(self, registry: HandlerRegistry) -> None:
        self.registry = registry

    def process_document(
        self,
        doc: Document,
        context: ProcessingContext,
        *,
        plugin_registry=None,
    ) -> None:
        context.bookmarks.register_headings(doc, context.navigation)
        context.captions.register_captions(doc, context)
        if doc.footnotes:
            context.footnotes.register_definitions(doc.footnotes, context.relationships)
        for child in doc.children:
            self.process(child, context)
        if doc.footnotes:
            context.footnotes.render_bodies(doc.footnotes, self, context)
        if plugin_registry is not None:
            from md2docx.plugin_api.validator import ValidationPhase

            plugin_registry.run_validators(ValidationPhase.SEMANTIC, doc)
        from md2docx.navigation.validator import validate_navigation

        nav_report = validate_navigation(context.navigation, context.bookmarks)
        if not nav_report.ok:
            from md2docx.navigation.errors import NavigationError

            raise NavigationError("; ".join(nav_report.errors))
        context.references.validate_pending_refs()

    def process(self, node: AstNode, context: ProcessingContext) -> None:
        handler = self.registry.get(node.type)
        result = handler.process(node, context, self)
        if result is not None:
            from md2docx.semantic.context import SemanticContext
            from md2docx.semantic.fragment import RichDocumentFragment
            from md2docx.semantic.renderer import SemanticRenderer

            if isinstance(result, RichDocumentFragment):
                SemanticRenderer.render_to_document(
                    result,
                    SemanticContext.from_processing_context(context),
                )
            else:
                raise TypeError(
                    f"handler for {node.type!r} returned unsupported value; "
                    "expected RichDocumentFragment or None"
                )

    def process_children(self, node: AstNode, context: ProcessingContext) -> None:
        children = getattr(node, "children", None) or []
        for child in children:
            self.process(child, context)
