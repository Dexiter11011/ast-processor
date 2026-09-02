"""Combined all-iterations integration test."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.ooxml.relationships import IMAGE_REL_TYPE
from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import R_NS, W_NS


def _paragraph_style(p: etree._Element) -> str | None:
    p_pr = p.find(f"{{{W_NS}}}pPr")
    if p_pr is None:
        return None
    p_style = p_pr.find(f"{{{W_NS}}}pStyle")
    if p_style is None:
        return None
    return p_style.get(f"{{{W_NS}}}val")


def _run_has_bold(run: etree._Element) -> bool:
    r_pr = run.find(f"{{{W_NS}}}rPr")
    return r_pr is not None and r_pr.find(f"{{{W_NS}}}b") is not None


def _run_has_italic(run: etree._Element) -> bool:
    r_pr = run.find(f"{{{W_NS}}}rPr")
    return r_pr is not None and r_pr.find(f"{{{W_NS}}}i") is not None


def test_all_iterations_combined(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "all-iterations.docx"
    convert_markdown_to_docx(fixtures_dir / "all-iterations.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
        rels_xml = zf.read("word/_rels/document.xml.rels").decode("utf-8")
        names = zf.namelist()
        core = etree.fromstring(zf.read("docProps/core.xml"))

    body = root.find(f"{{{W_NS}}}body")
    assert body is not None
    paragraphs = [c for c in body if c.tag == f"{{{W_NS}}}p"]
    # 12 content + 1 hr + 1 image + 1 alt + 1 code block + 2 blockquote + 3 bullet + 1 sep + 3 ordered + 1 sep + 3 nested + 9 table seps + 2 inline/unicode + 8 escaping = 48
    assert len(paragraphs) == 48
    assert any(name.startswith("word/media/image1.") for name in names)
    assert core.find("{http://purl.org/dc/elements/1.1/}title").text == "All Iterations Smoke Test"
    assert core.find("{http://purl.org/dc/elements/1.1/}creator").text == "md2docx"

    texts = [p.find(f".//{{{W_NS}}}t").text for p in paragraphs if p.find(f".//{{{W_NS}}}t") is not None]
    assert "Hello world" in texts
    assert "First paragraph." in texts
    assert "Third paragraph." in texts
    assert "Heading 1" in texts
    assert "Heading 3" in texts

    heading_styles = [
        style
        for p in paragraphs
        if (style := _paragraph_style(p)) in ("Heading1", "Heading2", "Heading3")
    ]
    assert heading_styles == ["Heading1", "Heading2", "Heading3"]

    bold_runs = [r for p in paragraphs for r in p.findall(f"{{{W_NS}}}r") if _run_has_bold(r)]
    assert len(bold_runs) == 9  # **world** + combo + nested inline (4) + **bold & <x>** (split at html token)
    standalone_bold = [r for r in bold_runs if not _run_has_italic(r) and r.find(f"{{{W_NS}}}t").text == "world"]
    assert len(standalone_bold) == 1

    italic_runs = [r for p in paragraphs for r in p.findall(f"{{{W_NS}}}r") if _run_has_italic(r)]
    assert len(italic_runs) == 5  # standalone italic + combo + nested italic + *italic & <y>* (split at html token)
    standalone_italic = [r for r in italic_runs if not _run_has_bold(r)]
    assert len(standalone_italic) == 3
    assert {r.find(f"{{{W_NS}}}t").text for r in standalone_italic} == {"world", "italic & ", "<y>"}

    combo_runs = [r for r in italic_runs if _run_has_bold(r)]
    assert len(combo_runs) == 2
    assert {r.find(f"{{{W_NS}}}t").text for r in combo_runs} == {"italic", "italic"}

    code_runs = [
        r
        for p in paragraphs
        for r in p.findall(f"{{{W_NS}}}r")
        if (r_pr := r.find(f"{{{W_NS}}}rPr")) is not None
        and (r_style := r_pr.find(f"{{{W_NS}}}rStyle")) is not None
        and r_style.get(f"{{{W_NS}}}val") == "Code"
    ]
    assert len(code_runs) == 3
    assert {r.find(f"{{{W_NS}}}t").text for r in code_runs} == {"npm install", "code", "code & <>"}

    hyperlinks = [p.find(f"{{{W_NS}}}hyperlink") for p in paragraphs if p.find(f"{{{W_NS}}}hyperlink") is not None]
    assert len(hyperlinks) == 2
    assert hyperlinks[0].get(f"{{{R_NS}}}id") == "rId2"
    assert hyperlinks[0].find(f".//{{{W_NS}}}t").text == "OpenAI"
    assert hyperlinks[1].get(f"{{{R_NS}}}id") == "rId4"
    assert hyperlinks[1].find(f".//{{{W_NS}}}t").text == "link"
    assert 'Target="https://example.com?q=a&amp;b=1"' in rels_xml
    assert 'Target="media/image1.png"' in rels_xml
    assert IMAGE_REL_TYPE in rels_xml

    hr_paragraphs = [
        p
        for p in paragraphs
        if (p_pr := p.find(f"{{{W_NS}}}pPr")) is not None and p_pr.find(f"{{{W_NS}}}pBdr") is not None
    ]
    assert len(hr_paragraphs) == 1
    assert hr_paragraphs[0].find(f".//{{{W_NS}}}t") is None

    drawing_paragraphs = [p for p in paragraphs if p.find(f".//{{{W_NS}}}drawing") is not None]
    assert len(drawing_paragraphs) == 1
    assert paragraphs[paragraphs.index(drawing_paragraphs[0]) + 1].find(f".//{{{W_NS}}}t").text == "Logo"

    code_block_paragraphs = [p for p in paragraphs if _paragraph_style(p) == "NoSpacing"]
    assert len(code_block_paragraphs) == 2
    code_block_texts = []
    for p in code_block_paragraphs:
        run = p.find(f"{{{W_NS}}}r")
        code_block_texts.append("".join(t.text or "" for t in run.findall(f"{{{W_NS}}}t")))
    assert code_block_texts == ['print("hello")', "x < y && z"]

    quote_paragraphs = [p for p in paragraphs if _paragraph_style(p) == "Quote"]
    assert len(quote_paragraphs) == 3
    quote_texts = [
        "".join(t.text or "" for t in p.findall(f".//{{{W_NS}}}t"))
        for p in quote_paragraphs
    ]
    assert quote_texts == [
        "Quote line one.",
        "Quote line two.",
        "quote & <z>",
    ]

    list_paragraphs = [p for p in paragraphs if _paragraph_style(p) == "ListParagraph"]
    assert len(list_paragraphs) == 10
    assert [p.find(f".//{{{W_NS}}}t").text for p in list_paragraphs[:3]] == ["One", "Two", "Three"]
    assert [p.find(f".//{{{W_NS}}}t").text for p in list_paragraphs[3:6]] == ["First", "Second", "Third"]
    assert [p.find(f".//{{{W_NS}}}t").text for p in list_paragraphs[6:9]] == ["Parent", "Child one", "Child two"]
    assert (
        "".join(t.text or "" for t in list_paragraphs[9].findall(f".//{{{W_NS}}}t"))
        == "item & <w>"
    )
    assert all(_paragraph_style(p) == "ListParagraph" for p in list_paragraphs)

    def _list_ilvl(p: etree._Element) -> str:
        p_pr = p.find(f"{{{W_NS}}}pPr")
        num_pr = p_pr.find(f"{{{W_NS}}}numPr") if p_pr is not None else None
        if num_pr is None:
            return "0"
        ilvl = num_pr.find(f"{{{W_NS}}}ilvl")
        return ilvl.get(f"{{{W_NS}}}val") if ilvl is not None else "0"

    assert _list_ilvl(list_paragraphs[6]) == "0"
    assert _list_ilvl(list_paragraphs[7]) == "1"
    assert _list_ilvl(list_paragraphs[8]) == "1"

    separators = [
        i
        for i, p in enumerate(paragraphs)
        if _paragraph_style(p) == "Normal" and p.find(f".//{{{W_NS}}}t") is None
    ]
    assert separators == [21, 25, 29, 30, 31, 32, 33, 34, 35, 36, 37]

    def _paragraph_text(p: etree._Element) -> str:
        return "".join(t.text or "" for t in p.findall(f".//{{{W_NS}}}t"))

    escaping_paragraphs = paragraphs[-8:]
    assert _paragraph_text(escaping_paragraphs[0]) == 'A & B <tag> "quote" \'apos\''
    assert _paragraph_text(escaping_paragraphs[1]) == "bold & <x>"
    assert _paragraph_text(escaping_paragraphs[2]) == "italic & <y>"
    escaping_code_runs = [
        r
        for r in escaping_paragraphs[3].findall(f"{{{W_NS}}}r")
        if (r_pr := r.find(f"{{{W_NS}}}rPr")) is not None
        and (r_style := r_pr.find(f"{{{W_NS}}}rStyle")) is not None
        and r_style.get(f"{{{W_NS}}}val") == "Code"
    ]
    assert len(escaping_code_runs) == 1
    assert escaping_code_runs[0].find(f"{{{W_NS}}}t").text == "code & <>"
    assert escaping_paragraphs[4].find(f"{{{W_NS}}}hyperlink").find(f".//{{{W_NS}}}t").text == "link"
    assert _paragraph_text(escaping_paragraphs[5]) == "x < y && z"
    assert _paragraph_text(escaping_paragraphs[6]) == "quote & <z>"
    assert _paragraph_text(escaping_paragraphs[7]) == "item & <w>"

    tables = [c for c in body if c.tag == f"{{{W_NS}}}tbl"]
    assert len(tables) == 9

    assert [t.text for t in tables[0].findall(f".//{{{W_NS}}}t")] == ["Name", "Age", "Bob", "20", "Ann", "30"]
    assert tables[0].find(f".//{{{W_NS}}}tblBorders") is not None
    header_p = tables[0].find(f".//{{{W_NS}}}tc").find(f"{{{W_NS}}}p")
    assert header_p.find(f".//{{{W_NS}}}b") is not None

    alignments = [jc.get(f"{{{W_NS}}}val") for jc in tables[1].findall(f".//{{{W_NS}}}jc")]
    assert alignments[:3] == ["left", "center", "right"]

    none_borders = tables[2].find(f".//{{{W_NS}}}tblBorders").find(f"{{{W_NS}}}top")
    assert none_borders.get(f"{{{W_NS}}}val") == "nil"

    double_borders = tables[3].find(f".//{{{W_NS}}}tblBorders").find(f"{{{W_NS}}}top")
    assert double_borders.get(f"{{{W_NS}}}val") == "double"

    shading_fills = [shd.get(f"{{{W_NS}}}fill") for shd in tables[4].findall(f".//{{{W_NS}}}shd")]
    assert "FFF2CC" in shading_fills
    assert "E2EFDA" in shading_fills

    centering_table = tables[5]
    assert "center" in [el.get(f"{{{W_NS}}}val") for el in centering_table.findall(f".//{{{W_NS}}}vAlign")]
    assert "center" in [el.get(f"{{{W_NS}}}val") for el in centering_table.findall(f".//{{{W_NS}}}jc")]

    horizontal_merge = tables[6]
    assert horizontal_merge.find(f".//{{{W_NS}}}gridSpan") is not None
    assert horizontal_merge.find(f".//{{{W_NS}}}gridSpan").get(f"{{{W_NS}}}val") == "2"

    vertical_merge = tables[7]
    v_merges = vertical_merge.findall(f".//{{{W_NS}}}vMerge")
    assert len([el for el in v_merges if el.get(f"{{{W_NS}}}val") == "continue"]) >= 2

    layout_table = tables[8]
    assert layout_table.find(f".//{{{W_NS}}}gridSpan") is not None
    assert layout_table.find(f".//{{{W_NS}}}shd") is not None

    all_text = " ".join(t.text or "" for t in root.findall(f".//{{{W_NS}}}t"))
    assert "table:" not in all_text
    assert "<!--" not in all_text
    assert "{bg:" not in all_text
    assert "^^" not in all_text
    assert "Привет мир — 日本語 — 😀" in all_text

    nested_paragraph = next(
        p
        for p in paragraphs
        if any(
            (t := r.find(f"{{{W_NS}}}t")) is not None and t.text == "bold, "
            for r in p.findall(f"{{{W_NS}}}r")
        )
    )
    nested_runs = nested_paragraph.findall(f"{{{W_NS}}}r")
    assert len(nested_runs) == 6
    assert nested_runs[4].find(f"{{{W_NS}}}t").text == "code"
    r_style = nested_runs[4].find(f".//{{{W_NS}}}rStyle")
    assert r_style is not None
    assert r_style.get(f"{{{W_NS}}}val") == "Code"
