"""Integration test for typed cross-reference validation."""

from __future__ import annotations

import pytest

from md2docx.ast.types import Document, Paragraph, Text
from md2docx.captions.kinds import CaptionKind
from md2docx.captions.model import CrossReferenceBlock
from md2docx.navigation.errors import ReferenceKindMismatchError
from md2docx.pipeline import convert_ast_to_docx
from md2docx.references.reference import CrossReference
from tests.figures_fixtures import build_single_table_document


def test_wrong_kind_cross_reference_fails(tmp_path):
    document = build_single_table_document()
    document.children.append(
        CrossReferenceBlock(
            reference=CrossReference(
                target="table-results",
                kind=CaptionKind.FIGURE,
                prefix="See ",
            )
        )
    )
    with pytest.raises(ReferenceKindMismatchError, match="not a figure target"):
        convert_ast_to_docx(document, tmp_path / "bad.docx")
