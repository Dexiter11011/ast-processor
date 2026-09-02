"""OOXML high-level API tests."""

from lxml import etree

from md2docx.ooxml import api
from md2docx.ooxml.document import OoxmlDocument
from tests.helpers import W_NS


def test_run_with_text_builds_paragraph():
    paragraph = api.paragraph([api.run(api.text("Hello"))])
    assert paragraph.tag == f"{{{W_NS}}}p"
    text_el = paragraph.find(f".//{{{W_NS}}}t")
    assert text_el is not None
    assert text_el.text == "Hello"


def test_document_add_paragraph_and_heading():
    doc = OoxmlDocument()
    doc.add_paragraph([api.run("Body")])
    doc.add_heading([api.run("Title")], style_id="Heading1")
    assert len(doc.body_children) == 2
    assert doc.body_children[1].find(f".//{{{W_NS}}}pStyle").get(f"{{{W_NS}}}val") == "Heading1"


def test_bold_and_italic_run_properties():
    run = api.run("x")
    api.bold(run)
    api.italic(run)
    r_pr = run.find(f"{{{W_NS}}}rPr")
    assert r_pr is not None
    assert r_pr.find(f"{{{W_NS}}}b") is not None
    assert r_pr.find(f"{{{W_NS}}}i") is not None


def test_hyperlink_wraps_runs():
    rel_id = "rId5"
    hyper = api.hyperlink([api.run("Click")], rel_id=rel_id)
    assert hyper.tag == f"{{{W_NS}}}hyperlink"
    assert hyper.get(f"{{http://schemas.openxmlformats.org/officeDocument/2006/relationships}}id") == rel_id


def test_internal_hyperlink_uses_anchor():
    hyper = api.hyperlink([api.run("Go")], anchor="intro")
    assert hyper.get(f"{{{W_NS}}}anchor") == "intro"
    assert hyper.get(f"{{http://schemas.openxmlformats.org/officeDocument/2006/relationships}}id") is None
