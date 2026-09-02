"""Page layout model tests."""

from md2docx.sections.definition import Orientation, PageLayout, PageMargins, PageSize


def test_a4_portrait_dimensions():
    layout = PageLayout.a4_portrait()
    assert layout.effective_size() == (11906, 16838)


def test_a4_landscape_swaps_dimensions():
    layout = PageLayout.a4_landscape()
    assert layout.effective_size() == (16838, 11906)
    assert layout.orientation == Orientation.LANDSCAPE


def test_letter_portrait_dimensions():
    layout = PageLayout.letter_portrait()
    assert layout.effective_size() == (12240, 15840)


def test_custom_margins():
    margins = PageMargins(720, 720, 720, 720)
    layout = PageLayout.a4_portrait(margins=margins)
    assert layout.margins == margins
