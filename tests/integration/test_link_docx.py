"""Link integration tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md2docx.ooxml.relationships import HYPERLINK_REL_TYPE
from md2docx.pipeline import convert_markdown_to_docx
from tests.helpers import R_NS, W_NS


def test_pipeline_link(tmp_path: Path, fixtures_dir: Path):
    output_path = tmp_path / "link.docx"
    convert_markdown_to_docx(fixtures_dir / "link.md", output_path)

    with zipfile.ZipFile(output_path, "r") as zf:
        doc_xml = zf.read("word/document.xml")
        rels_xml = zf.read("word/_rels/document.xml.rels").decode("utf-8")
        root = etree.fromstring(doc_xml)

    p = root.find(f".//{{{W_NS}}}p")
    hyper = p.find(f"{{{W_NS}}}hyperlink")
    assert hyper is not None
    rel_id = hyper.get(f"{{{R_NS}}}id")
    assert rel_id == "rId2"
    assert hyper.find(f".//{{{W_NS}}}t").text == "OpenAI"

    assert f'Id="{rel_id}"' in rels_xml
    assert 'Target="https://openai.com"' in rels_xml
    assert 'TargetMode="External"' in rels_xml
    assert HYPERLINK_REL_TYPE in rels_xml

    plain_runs = [r for r in p.findall(f"{{{W_NS}}}r")]
    assert len(plain_runs) == 2
    assert plain_runs[0].find(f"{{{W_NS}}}t").text == "Visit "
    assert plain_runs[1].find(f"{{{W_NS}}}t").text == "."
