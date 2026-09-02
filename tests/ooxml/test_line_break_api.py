"""OOXML line break API tests."""

from md2docx.ooxml import api
from tests.helpers import W_NS


def test_line_break_api():
    run = api.line_break()
    assert run.find(f"{{{W_NS}}}br") is not None
