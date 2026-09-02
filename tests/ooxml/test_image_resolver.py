"""Image path resolution tests."""

from pathlib import Path

import pytest

from md2docx.ooxml.image_resolver import resolve_image_path
from md2docx.processor.errors import ImagePathError


def test_resolve_relative_image(fixtures_dir: Path):
    path = resolve_image_path("logo.png", fixtures_dir)
    assert path == (fixtures_dir / "logo.png").resolve()
    assert path.is_file()


def test_reject_path_outside_source_dir(fixtures_dir: Path):
    with pytest.raises(ImagePathError, match="not allowed"):
        resolve_image_path("../outside/logo.png", fixtures_dir)


def test_reject_absolute_path_outside_source_dir(fixtures_dir: Path, tmp_path: Path):
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"\x89PNG\r\n\x1a\n")
    with pytest.raises(ImagePathError, match="not allowed"):
        resolve_image_path(str(outside), fixtures_dir)
