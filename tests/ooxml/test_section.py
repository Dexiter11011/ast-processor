"""OOXML section builder tests."""

from lxml import etree

from md2docx.ooxml.section import build_sect_pr
from md2docx.sections.definition import PageLayout, PageMargins
from tests.helpers import W_NS


def test_build_sect_pr_a4_portrait():
    root = build_sect_pr(PageLayout.a4_portrait())
    pg_sz = root.find(f"{{{W_NS}}}pgSz")
    assert pg_sz is not None
    assert pg_sz.get(f"{{{W_NS}}}w") == "11906"
    assert pg_sz.get(f"{{{W_NS}}}h") == "16838"
    assert pg_sz.get(f"{{{W_NS}}}orient") is None


def test_build_sect_pr_landscape():
    root = build_sect_pr(PageLayout.a4_landscape())
    pg_sz = root.find(f"{{{W_NS}}}pgSz")
    assert pg_sz.get(f"{{{W_NS}}}w") == "16838"
    assert pg_sz.get(f"{{{W_NS}}}h") == "11906"
    assert pg_sz.get(f"{{{W_NS}}}orient") == "landscape"


def test_build_sect_pr_margins():
    layout = PageLayout.a4_portrait(margins=PageMargins(720, 720, 720, 720))
    root = build_sect_pr(layout)
    pg_mar = root.find(f"{{{W_NS}}}pgMar")
    assert pg_mar is not None
    assert pg_mar.get(f"{{{W_NS}}}top") == "720"


def test_build_sect_pr_header_footer_refs():
    root = build_sect_pr(PageLayout.a4_portrait(), header_rel_id="rId5", footer_rel_id="rId6")
    header = root.find(f"{{{W_NS}}}headerReference")
    footer = root.find(f"{{{W_NS}}}footerReference")
    assert header is not None
    assert footer is not None
