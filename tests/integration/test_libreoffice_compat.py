"""LibreOffice headless compatibility (optional)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from md2docx.pipeline import convert_markdown_to_docx

LIBREOFFICE = shutil.which("libreoffice") or shutil.which("soffice")


@pytest.mark.skipif(LIBREOFFICE is None, reason="LibreOffice is not installed")
@pytest.mark.parametrize(
    "fixture_name",
    ["empty", "integration-article"],
)
def test_libreoffice_converts_docx_to_pdf_without_error(
    fixture_name: str,
    fixtures_dir: Path,
    tmp_path: Path,
):
    docx_path = tmp_path / f"{fixture_name}.docx"
    convert_markdown_to_docx(fixtures_dir / f"{fixture_name}.md", docx_path)
    out_dir = tmp_path / "lo-out"
    out_dir.mkdir()
    result = subprocess.run(
        [
            LIBREOFFICE,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(out_dir),
            str(docx_path),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    pdfs = list(out_dir.glob("*.pdf"))
    assert pdfs
