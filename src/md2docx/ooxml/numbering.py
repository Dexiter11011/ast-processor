"""In-memory numbering.xml builder for list paragraphs."""

from __future__ import annotations

from lxml import etree

from md2docx.ooxml.xml_builder import W_NS, serialize, w_attr, w_tag

BULLET_NUM_ID = 1
ORDERED_NUM_ID = 2
BULLET_ABSTRACT_ID = 0
ORDERED_ABSTRACT_ID = 1
MAX_LIST_LEVEL = 9
DEFAULT_LIST_PARAGRAPH_STYLE = "ListParagraph"


class NumberingManager:
    """Build Word-compatible numbering definitions for bullet/ordered lists."""

    def __init__(self, *, list_paragraph_style_id: str = DEFAULT_LIST_PARAGRAPH_STYLE) -> None:
        self._list_paragraph_style_id = list_paragraph_style_id
        self._initialized = False
        self._root: etree._Element | None = None
        self._next_num_id = 3

    def num_id_for_list(self, *, ordered: bool) -> int:
        """Return the canonical numId used by list styles (legacy fallback)."""
        self._ensure_initialized()
        return ORDERED_NUM_ID if ordered else BULLET_NUM_ID

    def allocate_num_id(
        self,
        *,
        ordered: bool,
        restart: bool = True,
        restart_ilvl: int = 0,
    ) -> int:
        """Allocate a numId; restart at ``restart_ilvl`` when restart=True."""
        self._ensure_initialized()
        abstract_id = ORDERED_ABSTRACT_ID if ordered else BULLET_ABSTRACT_ID
        num_id = self._next_num_id
        self._next_num_id += 1
        self._ensure_root().append(
            _build_num(num_id, abstract_id, restart=restart, restart_ilvl=restart_ilvl)
        )
        return num_id

    def _ensure_root(self) -> etree._Element:
        if self._root is None:
            self._root = etree.Element(w_tag("numbering"), nsmap={"w": W_NS})
        return self._root

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        root = self._ensure_root()
        root.append(_build_abstract_num(BULLET_ABSTRACT_ID, ordered=False, list_paragraph_style_id=self._list_paragraph_style_id))
        root.append(_build_abstract_num(ORDERED_ABSTRACT_ID, ordered=True, list_paragraph_style_id=self._list_paragraph_style_id))
        root.append(_build_num(BULLET_NUM_ID, BULLET_ABSTRACT_ID))
        root.append(_build_num(ORDERED_NUM_ID, ORDERED_ABSTRACT_ID))
        self._initialized = True

    def to_bytes(self) -> bytes | None:
        if self._root is None:
            return None
        return serialize(self._root)


def _build_level(level: int, *, ordered: bool, list_paragraph_style_id: str) -> etree._Element:
    lvl = etree.Element(w_tag("lvl"))
    lvl.set(w_attr("ilvl"), str(level))
    start = etree.SubElement(lvl, w_tag("start"))
    start.set(w_attr("val"), "1")
    num_fmt = etree.SubElement(lvl, w_tag("numFmt"))
    num_fmt.set(w_attr("val"), "decimal" if ordered else "bullet")
    p_style = etree.SubElement(lvl, w_tag("pStyle"))
    p_style.set(w_attr("val"), list_paragraph_style_id)
    lvl_text = etree.SubElement(lvl, w_tag("lvlText"))
    lvl_text.set(w_attr("val"), f"%{level + 1}." if ordered else "\uf0b7")
    jc = etree.SubElement(lvl, w_tag("lvlJc"))
    jc.set(w_attr("val"), "left")
    left = 360 * (level + 1)
    p_pr = etree.SubElement(lvl, w_tag("pPr"))
    tabs = etree.SubElement(p_pr, w_tag("tabs"))
    tab = etree.SubElement(tabs, w_tag("tab"))
    tab.set(w_attr("val"), "num")
    tab.set(w_attr("pos"), str(left))
    ind = etree.SubElement(p_pr, w_tag("ind"))
    ind.set(w_attr("left"), str(left))
    ind.set(w_attr("hanging"), "360")
    if not ordered:
        r_pr = etree.SubElement(lvl, w_tag("rPr"))
        fonts = etree.SubElement(r_pr, w_tag("rFonts"))
        fonts.set(w_attr("ascii"), "Symbol")
        fonts.set(w_attr("hAnsi"), "Symbol")
        fonts.set(w_attr("hint"), "default")
    return lvl


def _build_abstract_num(abstract_id: int, *, ordered: bool, list_paragraph_style_id: str) -> etree._Element:
    abstract_num = etree.Element(w_tag("abstractNum"))
    abstract_num.set(w_attr("abstractNumId"), str(abstract_id))
    nsid = etree.SubElement(abstract_num, w_tag("nsid"))
    nsid.set(w_attr("val"), "A1B2C3D4" if ordered else "E5F6A7B8")
    multi = etree.SubElement(abstract_num, w_tag("multiLevelType"))
    multi.set(w_attr("val"), "multilevel")
    tmpl = etree.SubElement(abstract_num, w_tag("tmpl"))
    tmpl.set(w_attr("val"), "C0FFEE01" if ordered else "C0FFEE00")
    for level in range(MAX_LIST_LEVEL):
        abstract_num.append(_build_level(level, ordered=ordered, list_paragraph_style_id=list_paragraph_style_id))
    return abstract_num


def _build_num(
    num_id: int,
    abstract_id: int,
    *,
    restart: bool = False,
    restart_ilvl: int = 0,
) -> etree._Element:
    num = etree.Element(w_tag("num"))
    num.set(w_attr("numId"), str(num_id))
    abstract_ref = etree.SubElement(num, w_tag("abstractNumId"))
    abstract_ref.set(w_attr("val"), str(abstract_id))
    if restart:
        lvl_override = etree.SubElement(num, w_tag("lvlOverride"))
        lvl_override.set(w_attr("ilvl"), str(restart_ilvl))
        start_override = etree.SubElement(lvl_override, w_tag("startOverride"))
        start_override.set(w_attr("val"), "1")
    return num
