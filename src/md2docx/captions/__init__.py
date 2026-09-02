"""Captions, figures, tables with captions, and sequence identity."""

from md2docx.captions.kinds import CaptionKind, SequenceKind
from md2docx.captions.model import Caption, CrossReferenceBlock, Figure, TableWithCaption
from md2docx.captions.naming import caption_bookmark_name
from md2docx.captions.sequence import SequenceManager

__all__ = [
    "Caption",
    "CaptionKind",
    "CaptionService",
    "CrossReferenceBlock",
    "Figure",
    "SequenceKind",
    "SequenceManager",
    "TableWithCaption",
    "caption_bookmark_name",
]


def __getattr__(name: str):
    if name == "CaptionService":
        from md2docx.captions.service import CaptionService

        return CaptionService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
