"""OOXML image helper tests."""

from pathlib import Path

from md2docx.ooxml.image import read_image_dimensions, scale_to_max_width


def test_read_png_dimensions(fixtures_dir: Path):
    png = (fixtures_dir / "logo.png").read_bytes()
    assert read_image_dimensions(png) == (2, 2)


def test_scale_to_max_width():
    width_emu, height_emu = scale_to_max_width(800, 600)
    assert width_emu == 4 * 914_400
    assert height_emu == int(600 * 9_525 * (4 * 914_400 / (800 * 9_525)))
