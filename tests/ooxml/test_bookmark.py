"""OOXML bookmark builder tests."""

from md2docx.ooxml import api
from md2docx.ooxml.bookmark import build_bookmark_end, build_bookmark_start
from tests.helpers import W_NS


def test_bookmark_start_and_end():
    start = build_bookmark_start("intro", 42)
    end = build_bookmark_end(42)
    assert start.tag == f"{{{W_NS}}}bookmarkStart"
    assert start.get(f"{{{W_NS}}}name") == "intro"
    assert start.get(f"{{{W_NS}}}id") == "42"
    assert end.get(f"{{{W_NS}}}id") == "42"


def test_heading_with_bookmark():
    para = api.heading([api.run("Title")], style_id="Heading1", bookmark_name="title", bookmark_id=1)
    starts = para.findall(f"{{{W_NS}}}bookmarkStart")
    ends = para.findall(f"{{{W_NS}}}bookmarkEnd")
    assert len(starts) == 1
    assert len(ends) == 1
    assert starts[0].get(f"{{{W_NS}}}name") == "title"
