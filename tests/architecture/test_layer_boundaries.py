"""Architecture layer boundary tests."""

from __future__ import annotations

import ast
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src" / "md2docx"


def _module_imports(module_path: Path) -> set[str]:
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def _python_files_in(relative_dir: str) -> list[Path]:
    root = SRC_ROOT / relative_dir
    return sorted(root.rglob("*.py"))


def test_ooxml_layer_does_not_import_parser_or_markdown():
    forbidden_prefixes = ("md2docx.parser", "markdown")
    violations: list[str] = []
    for path in _python_files_in("ooxml"):
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_package_layer_does_not_import_parser():
    forbidden_prefixes = ("md2docx.parser",)
    violations: list[str] = []
    for path in _python_files_in("ooxml"):
        if path.name != "package.py":
            continue
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_ast_processor_does_not_import_ooxml():
    path = SRC_ROOT / "processor" / "ast_processor.py"
    forbidden_prefixes = ("md2docx.ooxml",)
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes)
    ]
    assert violations == []


def test_ast_processor_does_not_import_concrete_handlers():
    processor_files = [
        SRC_ROOT / "processor" / "ast_processor.py",
        SRC_ROOT / "processor" / "registry.py",
    ]
    forbidden_prefixes = ("md2docx.elements",)
    violations: list[str] = []
    for path in processor_files:
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.name} imports {imported}")
    assert violations == []


def test_parser_does_not_import_handlers_or_ooxml():
    forbidden_prefixes = ("md2docx.elements", "md2docx.ooxml", "md2docx.processor")
    violations: list[str] = []
    for path in _python_files_in("parser"):
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_handlers_use_shared_context_managers():
    """Handlers must receive shared resources via ProcessingContext only."""
    handler_dir = SRC_ROOT / "elements"
    forbidden = (
        "md2docx.ooxml.relationships",
        "md2docx.ooxml.numbering",
        "md2docx.ooxml.document",
        "md2docx.processor.media_manager",
        "md2docx.processor.style_manager",
    )
    skip = {"__init__.py", "base.py", "inline_format.py", "inline_runs.py"}
    violations: list[str] = []
    for path in handler_dir.glob("*.py"):
        if path.name in skip:
            continue
        for imported in _module_imports(path):
            if imported in forbidden:
                violations.append(f"{path.name} imports {imported}")
    assert violations == []


def test_handlers_use_ooxml_api_not_low_level_builders():
    """Handlers must use md2docx.ooxml.api instead of low-level builder modules."""
    handler_dir = SRC_ROOT / "elements"
    forbidden_prefixes = (
        "md2docx.ooxml.paragraph",
        "md2docx.ooxml.run",
        "md2docx.ooxml.text",
        "md2docx.ooxml.heading",
        "md2docx.ooxml.hyperlink",
        "md2docx.ooxml.bookmark",
        "md2docx.ooxml.field",
        "md2docx.ooxml.line_break",
        "md2docx.ooxml.table",
        "md2docx.ooxml.horizontal_rule",
        "md2docx.ooxml.code_block",
        "md2docx.ooxml.image",
        "md2docx.ooxml.xml_builder",
    )
    allowed_ooxml = {"md2docx.ooxml.api", "md2docx.ooxml.image_resolver"}
    skip = {"__init__.py", "base.py", "inline_runs.py"}
    violations: list[str] = []
    for path in handler_dir.glob("*.py"):
        if path.name in skip:
            continue
        for imported in _module_imports(path):
            if not imported.startswith("md2docx.ooxml"):
                continue
            if imported in allowed_ooxml:
                continue
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.name} imports {imported}")
    assert violations == []


def test_only_context_creates_shared_managers_in_processor_layer():
    """RelationshipManager and friends are constructed in context.create_default."""
    forbidden_types = (
        "RelationshipManager",
        "StyleManager",
        "MediaManager",
        "NumberingManager",
    )
    violations: list[str] = []
    for path in _python_files_in("processor"):
        if path.name == "context.py":
            continue
        source = path.read_text(encoding="utf-8")
        for name in forbidden_types:
            if f"{name}()" in source:
                violations.append(f"{path.relative_to(SRC_ROOT)} constructs {name}()")
    assert violations == []


def test_ooxml_does_not_build_xml_via_string_templates():
    """OOXML parts must use lxml builders, not f-string/XML concatenation."""
    forbidden_patterns = (
        'f"<',
        "f'<",
        'f"""<',
        "f'''<",
        'return f"<',
        "return f'<",
        "${",
    )
    violations: list[str] = []
    for path in _python_files_in("ooxml"):
        if path.name == "xml_builder.py":
            continue
        source = path.read_text(encoding="utf-8")
        for pattern in forbidden_patterns:
            if pattern in source:
                violations.append(f"{path.relative_to(SRC_ROOT)} contains {pattern!r}")
    assert violations == []


def test_ooxml_does_not_import_elements_or_parser():
    forbidden_prefixes = ("md2docx.elements", "md2docx.parser")
    violations: list[str] = []
    for path in _python_files_in("ooxml"):
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_inline_handlers_do_not_call_bold_or_italic_api():
    handler_dir = SRC_ROOT / "elements"
    targets = {"strong.py", "emphasis.py"}
    forbidden = ("api.bold", "api.italic")
    violations: list[str] = []
    for name in targets:
        source = (handler_dir / name).read_text(encoding="utf-8")
        for token in forbidden:
            if token in source:
                violations.append(f"{name} contains {token}")
    assert violations == []


def test_formatting_applied_via_run_from_formatting():
    handler_dir = SRC_ROOT / "elements"
    text_source = (handler_dir / "text.py").read_text(encoding="utf-8")
    assert "run_from_formatting" in text_source
    assert "api.bold" not in text_source
    assert "api.italic" not in text_source


def test_validation_does_not_import_handlers_or_parser():
    forbidden_prefixes = ("md2docx.elements", "md2docx.parser", "md2docx.processor")
    violations: list[str] = []
    for path in _python_files_in("validation"):
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_styles_package_does_not_import_parser_ast_or_elements():
    forbidden_prefixes = ("md2docx.parser", "md2docx.ast", "md2docx.elements")
    violations: list[str] = []
    styles_root = SRC_ROOT / "styles"
    for path in sorted(styles_root.rglob("*.py")):
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_styles_xml_writer_does_not_import_handlers_or_parser():
    path = SRC_ROOT / "ooxml" / "styles_xml_writer.py"
    forbidden_prefixes = ("md2docx.parser", "md2docx.ast", "md2docx.elements")
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes)
    ]
    assert violations == []


def test_render_context_does_not_import_style_registry():
    path = SRC_ROOT / "processor" / "inline_formatting.py"
    forbidden = ("md2docx.styles", "StyleRegistry", "StyleManager")
    source = path.read_text(encoding="utf-8")
    violations = [token for token in forbidden if token in source]
    assert violations == []


def test_handlers_do_not_contain_hardcoded_visual_style_literals():
    handler_dir = SRC_ROOT / "elements"
    forbidden_patterns = (
        "font_size =",
        "font_family =",
        "spacing_before =",
        "spacing_after =",
        '"Calibri"',
        '"Consolas"',
        '"Courier New"',
    )
    skip = {"__init__.py", "base.py", "inline_format.py", "inline_runs.py"}
    violations: list[str] = []
    for path in handler_dir.glob("*.py"):
        if path.name in skip:
            continue
        source = path.read_text(encoding="utf-8")
        for pattern in forbidden_patterns:
            if pattern in source:
                violations.append(f"{path.name} contains {pattern!r}")
    assert violations == []


def test_list_handler_does_not_hardcode_ooxml_list_style_ids():
    path = SRC_ROOT / "elements" / "list.py"
    source = path.read_text(encoding="utf-8")
    forbidden = ('"ListBullet"', '"ListNumber"', "ListBullet", "ListNumber")
    violations = [token for token in forbidden if token in source]
    assert violations == []


def test_numbering_manager_does_not_import_parser_ast_or_elements():
    path = SRC_ROOT / "ooxml" / "numbering.py"
    forbidden_prefixes = ("md2docx.parser", "md2docx.ast", "md2docx.elements")
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes)
    ]
    assert violations == []


def test_table_handler_does_not_build_raw_ooxml():
    path = SRC_ROOT / "elements" / "table.py"
    source = path.read_text(encoding="utf-8")
    forbidden = ("etree.SubElement", "w:tbl", "w:tr", "w:tc")
    violations = [token for token in forbidden if token in source]
    assert violations == []


def test_section_manager_does_not_import_parser_ast_or_elements():
    path = SRC_ROOT / "sections" / "manager.py"
    forbidden_prefixes = ("md2docx.parser", "md2docx.ast", "md2docx.elements")
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes)
    ]
    assert violations == []


def test_layout_handlers_do_not_emit_raw_section_xml():
    handler_names = ("page_break.py", "section_break.py", "header_directive.py", "footer_directive.py")
    forbidden = ("w:sectPr", "w:pgSz", "w:pgMar", "w:hdr", "w:ftr", "etree.SubElement")
    violations: list[str] = []
    for name in handler_names:
        source = (SRC_ROOT / "elements" / name).read_text(encoding="utf-8")
        for token in forbidden:
            if token in source:
                violations.append(f"{name} contains {token!r}")
    assert violations == []


def test_styles_package_does_not_import_sections():
    forbidden_prefixes = ("md2docx.sections",)
    violations: list[str] = []
    styles_root = SRC_ROOT / "styles"
    for path in sorted(styles_root.rglob("*.py")):
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_bookmark_manager_does_not_import_parser_ast_or_elements():
    path = SRC_ROOT / "references" / "manager.py"
    forbidden_prefixes = ("md2docx.parser", "md2docx.elements")
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes)
    ]
    assert violations == []


def test_toc_manager_does_not_import_parser_ast_or_elements():
    path = SRC_ROOT / "toc" / "manager.py"
    forbidden_prefixes = ("md2docx.parser", "md2docx.ast", "md2docx.elements")
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes)
    ]
    assert violations == []


def test_relationship_manager_does_not_import_ast():
    path = SRC_ROOT / "ooxml" / "relationships.py"
    forbidden_prefixes = ("md2docx.ast", "md2docx.parser", "md2docx.elements")
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes)
    ]
    assert violations == []


def test_style_registry_does_not_import_references_or_toc():
    forbidden_prefixes = ("md2docx.references", "md2docx.toc")
    violations: list[str] = []
    for path in sorted((SRC_ROOT / "styles").rglob("*.py")):
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_link_handler_does_not_import_relationships_module():
    path = SRC_ROOT / "elements" / "link.py"
    forbidden = ("md2docx.ooxml.relationships",)
    violations = [
        imported
        for imported in _module_imports(path)
        if imported in forbidden
    ]
    assert violations == []


def test_reference_handlers_do_not_emit_raw_bookmark_or_field_xml():
    handler_names = ("link.py", "heading.py", "toc.py")
    forbidden = ("bookmarkStart", "bookmarkEnd", "fldChar", "fldSimple", "w:anchor", "etree.SubElement")
    violations: list[str] = []
    for name in handler_names:
        source = (SRC_ROOT / "elements" / name).read_text(encoding="utf-8")
        for token in forbidden:
            if token in source:
                violations.append(f"{name} contains {token!r}")
    assert violations == []


def test_handlers_forbidden_ooxml_builders_include_bookmark_and_field():
    handler_dir = SRC_ROOT / "elements"
    forbidden_prefixes = (
        "md2docx.ooxml.paragraph",
        "md2docx.ooxml.run",
        "md2docx.ooxml.text",
        "md2docx.ooxml.heading",
        "md2docx.ooxml.hyperlink",
        "md2docx.ooxml.bookmark",
        "md2docx.ooxml.field",
        "md2docx.ooxml.line_break",
        "md2docx.ooxml.table",
        "md2docx.ooxml.horizontal_rule",
        "md2docx.ooxml.code_block",
        "md2docx.ooxml.image",
        "md2docx.ooxml.xml_builder",
    )
    allowed_ooxml = {"md2docx.ooxml.api", "md2docx.ooxml.image_resolver"}
    skip = {"__init__.py", "base.py", "inline_runs.py"}
    violations: list[str] = []
    for path in handler_dir.glob("*.py"):
        if path.name in skip:
            continue
        for imported in _module_imports(path):
            if not imported.startswith("md2docx.ooxml"):
                continue
            if imported in allowed_ooxml:
                continue
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.name} imports {imported}")
    assert violations == []


def test_gfm_handlers_do_not_emit_raw_ooxml_literals():
    handler_names = ("strikethrough.py", "line_break.py")
    forbidden = ("w:strike", "w:br", "etree.SubElement", "bookmarkStart")
    violations: list[str] = []
    for name in handler_names:
        source = (SRC_ROOT / "elements" / name).read_text(encoding="utf-8")
        for token in forbidden:
            if token in source:
                violations.append(f"{name} contains {token!r}")
    assert violations == []


def test_parser_does_not_import_ooxml():
    forbidden_prefixes = ("md2docx.ooxml",)
    violations: list[str] = []
    for path in sorted((SRC_ROOT / "parser").rglob("*.py")):
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_theme_resolver_does_not_import_ooxml_or_handlers():
    path = SRC_ROOT / "styles" / "resolver.py"
    forbidden_prefixes = ("md2docx.ooxml", "md2docx.elements", "md2docx.parser", "md2docx.ast")
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes) or "etree" in imported
    ]
    assert violations == []


def test_theme_package_does_not_import_parser_ast_or_elements():
    forbidden_prefixes = ("md2docx.parser", "md2docx.ast", "md2docx.elements")
    violations: list[str] = []
    for path in sorted((SRC_ROOT / "styles").rglob("*.py")):
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_handlers_do_not_import_concrete_themes():
    handler_dir = SRC_ROOT / "elements"
    forbidden = ("AlternativeTestTheme", "alternative_test_theme", "DefaultTheme", "YamlDocumentTheme")
    skip = {"__init__.py", "base.py", "inline_format.py", "inline_runs.py"}
    violations: list[str] = []
    for path in handler_dir.glob("*.py"):
        if path.name in skip:
            continue
        source = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in source:
                violations.append(f"{path.name} contains {token!r}")
    assert violations == []


def test_themes_package_does_not_import_parser_ast_elements_or_ooxml():
    forbidden_prefixes = ("md2docx.parser", "md2docx.ast", "md2docx.elements", "md2docx.ooxml")
    violations: list[str] = []
    themes_root = SRC_ROOT / "themes"
    for path in sorted(themes_root.rglob("*.py")):
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_style_registry_does_not_import_themes_package():
    forbidden_prefixes = ("md2docx.themes",)
    violations: list[str] = []
    for path in sorted((SRC_ROOT / "styles").rglob("*.py")):
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_pipeline_does_not_import_yaml():
    path = SRC_ROOT / "pipeline.py"
    imports = _module_imports(path)
    assert "yaml" not in imports
    assert not any(item.startswith("md2docx.themes") for item in imports)


def test_cli_does_not_import_yaml():
    path = SRC_ROOT / "cli" / "main.py"
    imports = _module_imports(path)
    assert "yaml" not in imports


def test_templates_core_modules_do_not_import_parser_ast_or_elements():
    forbidden_prefixes = ("md2docx.parser", "md2docx.ast", "md2docx.elements")
    core_modules = (
        SRC_ROOT / "templates" / "reader.py",
        SRC_ROOT / "templates" / "package.py",
        SRC_ROOT / "templates" / "insertion.py",
        SRC_ROOT / "templates" / "context.py",
        SRC_ROOT / "templates" / "placeholders.py",
        SRC_ROOT / "templates" / "placeholder_parser.py",
    )
    violations: list[str] = []
    for path in core_modules:
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_templates_reader_and_package_do_not_import_ooxml():
    forbidden_prefixes = ("md2docx.ooxml",)
    core_modules = (
        SRC_ROOT / "templates" / "reader.py",
        SRC_ROOT / "templates" / "package.py",
    )
    violations: list[str] = []
    for path in core_modules:
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_templates_package_does_not_import_parser_ast_elements_or_ooxml():
    forbidden_prefixes = ("md2docx.parser", "md2docx.ast", "md2docx.elements")
    skip = {"merger.py", "style_merge.py", "content_types_merge.py", "context_builder.py"}
    violations: list[str] = []
    templates_root = SRC_ROOT / "templates"
    for path in sorted(templates_root.rglob("*.py")):
        if path.name in skip:
            continue
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_templates_package_does_not_import_yaml():
    forbidden = ("yaml", "md2docx.themes")
    violations: list[str] = []
    for path in sorted((SRC_ROOT / "templates").rglob("*.py")):
        for imported in _module_imports(path):
            if imported in forbidden or imported.startswith("md2docx.themes"):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_theme_loader_does_not_import_templates_package():
    path = SRC_ROOT / "themes" / "loader.py"
    forbidden_prefixes = ("md2docx.templates",)
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes)
    ]
    assert violations == []


def test_placeholder_parser_does_not_import_ast_ooxml_or_zip():
    path = SRC_ROOT / "templates" / "placeholder_parser.py"
    forbidden_prefixes = ("md2docx.ast", "md2docx.ooxml", "md2docx.parser", "zipfile")
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes) or imported == "zipfile"
    ]
    assert violations == []


def test_document_context_does_not_import_template_package():
    path = SRC_ROOT / "templates" / "context.py"
    forbidden_prefixes = (
        "md2docx.templates.package",
        "md2docx.templates.reader",
        "md2docx.parser",
        "md2docx.ast",
        "md2docx.fields",
    )
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes)
    ]
    assert violations == []


def test_fields_parser_does_not_import_ooxml_ast_or_parser():
    path = SRC_ROOT / "fields" / "parser.py"
    forbidden_prefixes = ("md2docx.ooxml", "md2docx.ast", "md2docx.parser", "zipfile")
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes) or imported == "zipfile"
    ]
    assert violations == []


def test_fields_manager_does_not_import_markdown_or_templates():
    path = SRC_ROOT / "fields" / "manager.py"
    forbidden_prefixes = ("md2docx.parser", "md2docx.templates", "markdown")
    violations = [
        imported
        for imported in _module_imports(path)
        if imported.startswith(forbidden_prefixes) or imported == "markdown"
    ]
    assert violations == []


def test_style_registry_does_not_import_templates_package():
    forbidden_prefixes = ("md2docx.templates",)
    violations: list[str] = []
    for path in sorted((SRC_ROOT / "styles").rglob("*.py")):
        for imported in _module_imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.relative_to(SRC_ROOT)} imports {imported}")
    assert violations == []


def test_caption_handlers_do_not_emit_raw_field_or_bookmark_xml():
    handler_names = ("figure.py", "table_with_caption.py", "cross_reference.py")
    forbidden = ("bookmarkStart", "bookmarkEnd", "fldChar", "fldSimple", "instrText", "etree.SubElement")
    violations: list[str] = []
    for name in handler_names:
        source = (SRC_ROOT / "elements" / name).read_text(encoding="utf-8")
        for token in forbidden:
            if token in source:
                violations.append(f"{name} contains {token!r}")
    assert violations == []


def test_captions_package_has_no_application_number_counters():
    forbidden_tokens = (
        "figure_number",
        "table_number",
        "counter +=",
        "counter+=",
        "_next_number",
        "number += 1",
        "number+=1",
    )
    violations: list[str] = []
    for path in sorted((SRC_ROOT / "captions").rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        for token in forbidden_tokens:
            if token in source:
                violations.append(f"{path.relative_to(SRC_ROOT)} contains {token!r}")
    assert violations == []
