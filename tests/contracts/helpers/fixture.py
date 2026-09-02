"""Reusable contract conversion fixture."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from md2docx.pipeline import convert_markdown_to_docx
from md2docx.plugin_api.registry import PluginRegistry
from md2docx.templates.reader import DocxPackageReader
from md2docx.themes.loader import ThemeLoader

from tests.contracts.helpers.semantic_docx import read_document_xml, read_styles_xml


@dataclass
class ContractDocumentFixture:
    """Convert Markdown with optional plugin/theme/template for contract tests."""

    tmp_path: Path
    plugin_paths: list[Path] = field(default_factory=list)
    theme_path: Path | None = None
    template_path: Path | None = None

    def convert(self, markdown: str, *, output_name: str = "output.docx") -> Path:
        source = self.tmp_path / "input.md"
        output = self.tmp_path / output_name
        source.write_text(markdown, encoding="utf-8")

        plugin_registry = None
        if self.plugin_paths:
            from md2docx.plugins.loader import load_plugins

            plugin_registry = load_plugins(self.plugin_paths)

        theme = ThemeLoader.load(self.theme_path) if self.theme_path else None
        template = (
            DocxPackageReader.load(self.template_path) if self.template_path else None
        )

        convert_markdown_to_docx(
            source,
            output,
            theme=theme,
            template=template,
            plugin_registry=plugin_registry,
        )
        return output

    def document_xml(self, output: Path) -> bytes:
        return read_document_xml(output)

    def styles_xml(self, output: Path) -> bytes:
        return read_styles_xml(output)
