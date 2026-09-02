"""Unit tests for template bookmark name remapping."""

from __future__ import annotations

from lxml import etree

from md2docx.fields.manager import FieldManager
from md2docx.ooxml import api
from md2docx.ooxml.xml_builder import w_attr, w_tag
from md2docx.references.manager import BookmarkManager
from md2docx.templates.bookmark_remap import (
    build_name_collision_remap,
    collect_fragment_bookmark_names,
    remap_bookmarks,
)


def _paragraph_with_bookmark(name: str, bookmark_id: int) -> etree._Element:
    para = api.paragraph([api.run("text")], style_id="Normal")
    start = etree.Element(w_tag("bookmarkStart"))
    start.set(w_attr("id"), str(bookmark_id))
    start.set(w_attr("name"), name)
    end = etree.Element(w_tag("bookmarkEnd"))
    end.set(w_attr("id"), str(bookmark_id))
    para.insert(0, start)
    para.append(end)
    return para


def test_build_name_collision_remap_uses_suffix():
    name_map = build_name_collision_remap(
        {"architecture", "figure-architecture"},
        {"architecture", "figure-architecture", "table-results"},
    )
    assert name_map["architecture"] == "architecture-1"
    assert name_map["figure-architecture"] == "figure-architecture-1"


def test_remap_bookmarks_rewrites_names_refs_and_anchors():
    bookmarks = BookmarkManager()
    bookmarks.register("architecture", bookmark_id=0)
    fields = FieldManager()
    ref_runs = fields.ref_field("architecture", bookmarks=bookmarks)
    para = api.paragraph([api.run("See "), *ref_runs], style_id="Normal")
    link_runs = [api.run("link")]
    para.append(api.hyperlink(link_runs, anchor="architecture"))
    start = etree.Element(w_tag("bookmarkStart"))
    start.set(w_attr("id"), "0")
    start.set(w_attr("name"), "architecture")
    end = etree.Element(w_tag("bookmarkEnd"))
    end.set(w_attr("id"), "0")
    para.insert(0, start)
    para.append(end)

    updated, remap = remap_bookmarks(
        [para],
        start_id=10,
        reserved_names={"architecture"},
    )
    assert remap.name_map == {"architecture": "architecture-1"}
    names = [
        node.get(w_attr("name"))
        for node in updated[0].iter(w_tag("bookmarkStart"))
    ]
    assert names == ["architecture-1"]
    anchors = [
        node.get(w_attr("anchor"))
        for node in updated[0].iter(w_tag("hyperlink"))
        if node.get(w_attr("anchor"))
    ]
    assert anchors == ["architecture-1"]
    instr = updated[0].find(f".//{w_tag('instrText')}")
    assert instr is not None
    assert "REF architecture-1" in (instr.text or "")


def test_collect_fragment_bookmark_names():
    para = _paragraph_with_bookmark("intro", 1)
    assert collect_fragment_bookmark_names([para]) == {"intro"}
