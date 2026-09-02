"""Unified document metadata resolution."""

from md2docx.metadata.resolved import ResolvedDocumentMetadata
from md2docx.metadata.resolver import MetadataResolver, resolve_document_metadata
from md2docx.metadata.sources import CliMetadataInput, FrontMatterMetadata

__all__ = [
    "CliMetadataInput",
    "FrontMatterMetadata",
    "MetadataResolver",
    "ResolvedDocumentMetadata",
    "resolve_document_metadata",
]
