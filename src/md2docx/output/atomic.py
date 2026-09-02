"""Atomic DOCX output writer."""

from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Callable

from md2docx.validation import validate_docx_bytes


class AtomicOutputError(OSError):
    """Raised when atomic output cannot be committed."""


class AtomicOutputWriter:
    """Write DOCX bytes to a temp file, validate, then atomically replace the target."""

    def __init__(
        self,
        final_path: Path,
        *,
        validate: bool = False,
        validator: Callable[[bytes], object] | None = None,
    ) -> None:
        self.final_path = final_path.resolve()
        self.validate = validate
        self._validator = validator or validate_docx_bytes
        self.final_path.parent.mkdir(parents=True, exist_ok=True)
        suffix = ".tmp"
        token = secrets.token_hex(8)
        self.temp_path = self.final_path.with_name(f".{self.final_path.name}.md2docx-{token}{suffix}")
        self._bytes: bytes | None = None
        self._committed = False
        self._aborted = False

    def write_bytes(self, data: bytes) -> None:
        if self._committed or self._aborted:
            raise AtomicOutputError("atomic output writer is already finalized")
        self._bytes = data
        self.temp_path.write_bytes(data)

    def commit(self) -> None:
        if self._committed or self._aborted:
            return
        if self._bytes is None:
            raise AtomicOutputError("no output bytes were written")
        if self.validate:
            try:
                report = self._validator(self._bytes)
            except Exception as exc:
                self.abort()
                raise AtomicOutputError(f"DOCX validation failed:\n{exc}") from exc
            ok = getattr(report, "ok", report)
            if not ok:
                messages = getattr(report, "format_messages", lambda: str(report))()
                self.abort()
                raise AtomicOutputError(f"DOCX validation failed:\n{messages}")
        try:
            os.replace(self.temp_path, self.final_path)
        except OSError as exc:
            self.abort()
            raise AtomicOutputError(str(exc)) from exc
        self._committed = True

    def abort(self) -> None:
        if self._aborted or self._committed:
            return
        self._aborted = True
        if self.temp_path.exists():
            try:
                self.temp_path.unlink()
            except OSError:
                pass

    def __enter__(self) -> AtomicOutputWriter:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc is not None:
            self.abort()
        elif not self._committed:
            self.abort()
