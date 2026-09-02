"""StyleDefinition model tests."""

from md2docx.styles.definition import ParagraphStyle, RunStyle, StyleDefinition


def test_style_definition_is_frozen():
    definition = StyleDefinition(
        semantic_id="normal",
        ooxml_id="Normal",
        name="Normal",
    )
    try:
        definition.name = "Changed"  # type: ignore[misc]
        assert False, "expected FrozenInstanceError"
    except AttributeError:
        pass


def test_paragraph_and_run_style_fields():
    definition = StyleDefinition(
        semantic_id="heading1",
        ooxml_id="Heading1",
        name="heading 1",
        based_on="normal",
        paragraph=ParagraphStyle(spacing_before=240, spacing_after=120),
        run=RunStyle(bold=True, font_size=32),
    )
    assert definition.paragraph is not None
    assert definition.paragraph.spacing_before == 240
    assert definition.run is not None
    assert definition.run.bold is True
