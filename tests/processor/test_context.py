"""ProcessingContext tests."""

from md2docx.ooxml.document import OoxmlDocument
from md2docx.ooxml.numbering import NumberingManager
from md2docx.ooxml.relationships import RelationshipManager
from md2docx.processor.context import ProcessingContext
from md2docx.processor.media_manager import MediaManager
from md2docx.processor.style_manager import StyleManager
from md2docx.sections.manager import SectionManager


def test_create_default_wires_all_shared_managers():
    ctx = ProcessingContext.create_default()

    assert isinstance(ctx.document, OoxmlDocument)
    assert isinstance(ctx.relationships, RelationshipManager)
    assert isinstance(ctx.styles, StyleManager)
    assert isinstance(ctx.numbering, NumberingManager)
    assert isinstance(ctx.media, MediaManager)
    assert isinstance(ctx.sections, SectionManager)


def test_create_default_registers_styles_relationship():
    ctx = ProcessingContext.create_default()
    assert any("styles.xml" in rel.target for rel in ctx.relationships.relationships)


def test_handlers_share_one_relationship_manager_instance():
    ctx = ProcessingContext.create_default()
    rel_id_a = ctx.relationships.add_external_hyperlink("https://example.com/a")
    rel_id_b = ctx.relationships.add_external_hyperlink("https://example.com/b")
    assert rel_id_a != rel_id_b
    assert len(ctx.relationships.relationships) >= 3
