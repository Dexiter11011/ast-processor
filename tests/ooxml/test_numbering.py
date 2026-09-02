"""NumberingManager unit tests."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.numbering import NumberingManager
from md2docx.ooxml.style_ids import LIST_PARAGRAPH
from tests.helpers import W_NS


def test_numbering_initializes_two_abstract_nums():
    manager = NumberingManager()
    manager.allocate_num_id(ordered=False)
    xml = manager.to_bytes()
    assert xml is not None
    root = etree.fromstring(xml)
    abstract_nums = root.findall(f"{{{W_NS}}}abstractNum")
    assert len(abstract_nums) == 2


def test_numbering_levels_use_list_paragraph_style():
    manager = NumberingManager()
    manager.allocate_num_id(ordered=True)
    root = etree.fromstring(manager.to_bytes())
    p_styles = root.findall(f".//{{{W_NS}}}lvl/{{{W_NS}}}pStyle")
    assert p_styles
    assert all(el.get(f"{{{W_NS}}}val") == LIST_PARAGRAPH for el in p_styles)


def test_allocate_num_id_restarts_at_nested_ilvl():
    manager = NumberingManager()
    manager.allocate_num_id(ordered=True, restart=True, restart_ilvl=1)
    root = etree.fromstring(manager.to_bytes())
    num = root.findall(f"{{{W_NS}}}num")[-1]
    override = num.find(f"{{{W_NS}}}lvlOverride")
    assert override is not None
    assert override.get(f"{{{W_NS}}}ilvl") == "1"
    start = override.find(f"{{{W_NS}}}startOverride")
    assert start is not None
    assert start.get(f"{{{W_NS}}}val") == "1"


def test_allocate_num_id_without_restart():
    manager = NumberingManager()
    first = manager.allocate_num_id(ordered=False, restart=False)
    second = manager.allocate_num_id(ordered=True, restart=False)
    root = etree.fromstring(manager.to_bytes())
    nums = root.findall(f"{{{W_NS}}}num")
    restart_ids = {
        num.get(f"{{{W_NS}}}numId")
        for num in nums
        if num.find(f"{{{W_NS}}}lvlOverride") is not None
    }
    assert str(first) not in restart_ids
    assert str(second) not in restart_ids
