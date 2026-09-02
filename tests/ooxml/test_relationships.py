"""RelationshipManager tests."""

from md2docx.ooxml.relationships import HYPERLINK_REL_TYPE, RelationshipManager


def test_add_external_hyperlink_allocates_rel_id():
    rels = RelationshipManager()
    rels.add_styles_relationship()
    rel_id = rels.add_external_hyperlink("https://openai.com")
    assert rel_id == "rId2"


def test_add_external_hyperlink_deduplicates_url():
    rels = RelationshipManager()
    rels.add_styles_relationship()
    first = rels.add_external_hyperlink("https://openai.com")
    second = rels.add_external_hyperlink("https://openai.com")
    assert first == second
    hyperlink_rels = [r for r in rels.relationships if r.rel_type == HYPERLINK_REL_TYPE]
    assert len(hyperlink_rels) == 1


def test_document_rels_escapes_ampersand_in_url():
    rels = RelationshipManager()
    rels.add_styles_relationship()
    rels.add_external_hyperlink("https://example.com?q=a&b=1")
    xml = rels.build_document_rels_xml().decode("utf-8")
    assert 'Target="https://example.com?q=a&amp;b=1"' in xml
    assert "Target=" in xml
    assert HYPERLINK_REL_TYPE in xml


def test_document_rels_contains_hyperlink():
    rels = RelationshipManager()
    rels.add_styles_relationship()
    rels.add_external_hyperlink("https://openai.com")
    xml = rels.build_document_rels_xml().decode("utf-8")
    assert 'Target="https://openai.com"' in xml
    assert 'TargetMode="External"' in xml
    assert HYPERLINK_REL_TYPE in xml
