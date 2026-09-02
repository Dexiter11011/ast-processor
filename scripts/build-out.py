#!/usr/bin/env python3
"""Run tests, build DOCX fixtures, extract packages to out/ as readable XML."""

from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
FIXTURES = (
    ("empty", ROOT / "tests" / "fixtures" / "empty.md"),
    ("hello-world", ROOT / "tests" / "fixtures" / "hello-world.md"),
    ("multiple-paragraphs", ROOT / "tests" / "fixtures" / "multiple-paragraphs.md"),
    ("headings", ROOT / "tests" / "fixtures" / "headings.md"),
    ("bold", ROOT / "tests" / "fixtures" / "bold.md"),
    ("italic", ROOT / "tests" / "fixtures" / "italic.md"),
    ("combinations", ROOT / "tests" / "fixtures" / "combinations.md"),
    ("inline-code", ROOT / "tests" / "fixtures" / "inline-code.md"),
    ("link", ROOT / "tests" / "fixtures" / "link.md"),
    ("unordered-list", ROOT / "tests" / "fixtures" / "unordered-list.md"),
    ("ordered-list", ROOT / "tests" / "fixtures" / "ordered-list.md"),
    ("nested-list", ROOT / "tests" / "fixtures" / "nested-list.md"),
    ("blockquote", ROOT / "tests" / "fixtures" / "blockquote.md"),
    ("horizontal-rule", ROOT / "tests" / "fixtures" / "horizontal-rule.md"),
    ("code-block", ROOT / "tests" / "fixtures" / "code-block.md"),
    ("xml-escaping", ROOT / "tests" / "fixtures" / "xml-escaping.md"),
    ("image", ROOT / "tests" / "fixtures" / "image.md"),
    ("table", ROOT / "tests" / "fixtures" / "table.md"),
    ("table-variants", ROOT / "tests" / "fixtures" / "table-variants.md"),
    ("advanced-tables", ROOT / "tests" / "fixtures" / "advanced-tables.md"),
    ("nested-inline", ROOT / "tests" / "fixtures" / "nested-inline.md"),
    ("escaping-edge-cases", ROOT / "tests" / "fixtures" / "escaping-edge-cases.md"),
    ("document-metadata", ROOT / "tests" / "fixtures" / "document-metadata.md"),
    ("integration-article", ROOT / "tests" / "fixtures" / "integration-article.md"),
    ("all-iterations", ROOT / "tests" / "fixtures" / "all-iterations.md"),
)


def _pretty_xml(data: bytes) -> str:
    try:
        root = etree.fromstring(data)
        return etree.tostring(root, pretty_print=True, encoding="unicode")
    except etree.XMLSyntaxError:
        return data.decode("utf-8")


def _extract_docx(docx_path: Path, dest: Path) -> list[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    extracted: list[Path] = []
    with zipfile.ZipFile(docx_path, "r") as zf:
        for name in zf.namelist():
            target = dest / name
            target.parent.mkdir(parents=True, exist_ok=True)
            raw = zf.read(name)
            if name.endswith(".xml") or name.endswith(".rels"):
                target.write_text(_pretty_xml(raw), encoding="utf-8")
            else:
                target.write_bytes(raw)
            extracted.append(target)
    return sorted(extracted)


def _write_build_results(*, test_output: str, builds: list[dict]) -> None:
    lines = [
        "# Build Results",
        "",
        "## Tests",
        "",
        "```",
        test_output.strip(),
        "```",
        "",
    ]

    for build in builds:
        docx_path: Path = build["docx_path"]
        extract_dir: Path = build["extract_dir"]
        extracted: list[Path] = build["extracted"]
        lines += [
            f"## {build['name']}",
            "",
            f"- **Archive:** `{docx_path.relative_to(ROOT)}`",
            f"- **Size:** {docx_path.stat().st_size} bytes",
            f"- **Extracted to:** `{extract_dir.relative_to(ROOT)}/`",
            "",
            "### Extracted package (unzipped)",
            "",
            "```text",
        ]
        for path in extracted:
            lines.append(str(path.relative_to(extract_dir)))
        lines += ["```", ""]

        for path in extracted:
            if path.suffix not in (".xml", ".rels") and path.name != ".rels":
                continue
            rel = path.relative_to(ROOT)
            content = path.read_text(encoding="utf-8").strip()
            lines += [f"### `{rel}`", "", "```xml", content, "```", ""]

    (OUT / "BUILD_RESULTS.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    test_output = result.stdout + result.stderr
    (OUT / "test-results.txt").write_text(test_output, encoding="utf-8")

    if result.returncode != 0:
        print(test_output, file=sys.stderr)
        return result.returncode

    from md2docx.pipeline import convert_markdown_to_docx

    builds: list[dict] = []
    for name, fixture in FIXTURES:
        docx_path = OUT / f"{name}.docx"
        convert_markdown_to_docx(fixture, docx_path)
        extract_dir = OUT / name
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extracted = _extract_docx(docx_path, extract_dir)
        builds.append(
            {
                "name": name,
                "docx_path": docx_path,
                "extract_dir": extract_dir,
                "extracted": extracted,
            }
        )
        print(f"Built → {docx_path.relative_to(ROOT)}")
        print(f"Extracted → {extract_dir.relative_to(ROOT)}/")

    _write_build_results(test_output=test_output, builds=builds)
    print("Report → out/BUILD_RESULTS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
