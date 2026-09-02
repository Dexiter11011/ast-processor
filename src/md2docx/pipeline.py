"""Markdown to DOCX conversion pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from md2docx.elements import create_default_registry
from md2docx.metadata.resolver import resolve_document_metadata
from md2docx.metadata.sources import CliMetadataInput, FrontMatterMetadata
from md2docx.ooxml.package import DocxPackageWriter
from md2docx.output.atomic import AtomicOutputWriter
from md2docx.parser.front_matter import parse_document_metadata, split_front_matter
from md2docx.parser.markdown_parser import MarkdownParser
from md2docx.parser.caption_transform import apply_caption_transform
from md2docx.parser.footnote_transform import apply_footnote_transform
from md2docx.processor.ast_processor import AstProcessor
from md2docx.processor.context import ProcessingContext
from md2docx.styles.theme import DefaultTheme, DocumentTheme
from md2docx.templates.context import DocumentContext
from md2docx.templates.context_builder import resolved_to_document_context
from md2docx.parser.navigation_transform import (
    strip_ast_types_for_template_regions,
    strip_navigation_for_template_regions,
)
from md2docx.templates.composition import navigation_region_names
from md2docx.templates.package import DOCUMENT_PART
from md2docx.templates.placeholder_scan import scan_body_placeholders
from md2docx.templates.merger import TemplateMerger
from md2docx.templates.package import TemplatePackage
from md2docx.plugin_api.registry import PluginRegistry
from md2docx.plugin_api.validator import ValidationPhase

if TYPE_CHECKING:
    pass


def _active_plugin_registry(plugin_registry: PluginRegistry | None) -> PluginRegistry:
    registry = plugin_registry or PluginRegistry.empty()
    if not registry.frozen:
        registry.freeze()
    return registry


def convert_markdown_to_docx(
    input_path: Path,
    output_path: Path,
    *,
    theme: DocumentTheme | None = None,
    template: TemplatePackage | None = None,
    document_context: DocumentContext | None = None,
    plugin_registry: PluginRegistry | None = None,
    cli_title: str | None = None,
    cli_author: str | None = None,
    cli_date: str | None = None,
    cli_subject: str | None = None,
    cli_keywords: str | None = None,
    update_fields: bool | None = None,
    validate_before_commit: bool = False,
) -> None:
    plugins = _active_plugin_registry(plugin_registry)
    source = input_path.read_text(encoding="utf-8")
    raw_metadata, body = split_front_matter(source)
    ast = MarkdownParser(plugins).parse(body, source_path=str(input_path))
    ast = apply_caption_transform(ast, source_path=str(input_path))
    ast = apply_footnote_transform(ast, source_path=str(input_path), source=body)
    ast.metadata = parse_document_metadata(raw_metadata)
    plugins.run_validators(ValidationPhase.PARSE, ast)
    if document_context is not None:
        active_context = document_context
        resolved = resolve_document_metadata(
            front_matter=FrontMatterMetadata(
                title=active_context.title,
                author=active_context.author,
                date=active_context.date,
                subject=active_context.subject,
                keywords=tuple(
                    part.strip()
                    for part in (active_context.keywords or "").split(",")
                    if part.strip()
                ),
            )
        )
    else:
        resolved = resolve_document_metadata(
            cli=CliMetadataInput(
                title=cli_title,
                author=cli_author,
                date=cli_date,
                subject=cli_subject,
                keywords=cli_keywords,
            ),
            front_matter=FrontMatterMetadata.from_raw(raw_metadata),
        )
        active_context = resolved_to_document_context(resolved)
    active_theme = theme or DefaultTheme.create()
    if template is None:
        context = ProcessingContext.create_default(
            source_dir=input_path.parent,
            theme=active_theme,
            plugin_registry=plugins,
        )
    else:
        context = ProcessingContext.create_for_template(
            source_dir=input_path.parent,
            theme=active_theme,
            plugin_registry=plugins,
        )
        extra_placeholders = plugins.plugin_placeholder_kinds()
        placeholders = scan_body_placeholders(
            template.get_part(DOCUMENT_PART),
            extra_placeholders=extra_placeholders,
        )
        navigation_regions = navigation_region_names(placeholders)
        plugin_region_names = {
            item.name for item in placeholders if item.name in extra_placeholders
        }
        ast = strip_navigation_for_template_regions(ast, navigation_regions)
        strip_types = plugins.strip_ast_types_for_regions(plugin_region_names)
        ast = strip_ast_types_for_template_regions(ast, strip_types)
    context.fields.set_metadata_display(title=resolved.title, author=resolved.author)
    context.resolved_metadata = resolved
    handler_registry = plugins.build_handler_registry() if plugins.loaded_plugins else create_default_registry()
    processor = AstProcessor(handler_registry)
    processor.process_document(ast, context, plugin_registry=plugins)
    with AtomicOutputWriter(output_path, validate=validate_before_commit) as writer:
        if template is None:
            DocxPackageWriter().write_from_context(
                context,
                writer,
                metadata=resolved,
                update_fields=update_fields,
            )
        else:
            parts = TemplateMerger.merge(
                template,
                context,
                theme=theme,
                document_context=active_context,
                resolved_metadata=resolved,
                update_fields=update_fields,
                plugin_registry=plugins,
            )
            DocxPackageWriter().write_package(parts, writer)
        writer.commit()
    plugins.run_validators(ValidationPhase.RENDER, context)


def convert_ast_to_docx(
    document,
    output_path: Path,
    *,
    source_dir: Path | None = None,
    theme: DocumentTheme | None = None,
    metadata=None,
    update_fields: bool | None = None,
    plugin_registry: PluginRegistry | None = None,
) -> None:
    """Convert a pre-built AST Document to DOCX (internal API / test fixtures)."""
    plugins = _active_plugin_registry(plugin_registry)
    active_theme = theme or DefaultTheme.create()
    context = ProcessingContext.create_default(
        source_dir=source_dir or Path.cwd(),
        theme=active_theme,
        plugin_registry=plugins,
    )
    handler_registry = plugins.build_handler_registry() if plugins.loaded_plugins else create_default_registry()
    processor = AstProcessor(handler_registry)
    processor.process_document(document, context, plugin_registry=plugins)
    DocxPackageWriter().write_from_context(
        context,
        output_path,
        metadata=metadata,
        update_fields=update_fields,
    )
