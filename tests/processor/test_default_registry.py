"""Default handler registry tests."""

from md2docx.elements import create_default_registry

EXPECTED_HANDLER_TYPES = frozenset(
    {
        "paragraph",
        "heading",
        "text",
        "strong",
        "emphasis",
        "strikethrough",
        "line_break",
        "inline_code",
        "link",
        "list",
        "list_item",
        "blockquote",
        "horizontal_rule",
        "page_break",
        "section_break",
        "header_directive",
        "footer_directive",
        "field_directive",
        "figure",
        "table_with_caption",
        "cross_reference",
        "table_of_contents",
        "list_of_figures",
        "list_of_tables",
        "code_block",
        "image",
        "table",
        "table_row",
        "table_cell",
        "footnote_reference",
        "definition_list",
    }
)


def test_default_registry_registers_all_built_in_handlers():
    registry = create_default_registry()
    assert registry.registered_types() == EXPECTED_HANDLER_TYPES
