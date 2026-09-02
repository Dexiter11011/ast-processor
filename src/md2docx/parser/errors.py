"""Parser errors for Markdown DSL transforms."""

from __future__ import annotations


class CaptionParseError(Exception):
    """Raised when caption directives are malformed or orphaned."""

    def __init__(self, message: str, *, line: int | None = None, path: str | None = None) -> None:
        self.line = line
        self.path = path
        if line is not None and path is not None:
            super().__init__(f"Error in {path}:{line}: {message}")
        elif line is not None:
            super().__init__(f"Error at line {line}: {message}")
        else:
            super().__init__(message)


class FootnoteParseError(Exception):
    """Raised when footnote references or definitions are invalid."""

    def __init__(self, message: str, *, line: int | None = None, path: str | None = None) -> None:
        self.line = line
        self.path = path
        if line is not None and path is not None:
            super().__init__(f"Error in {path}:{line}: {message}")
        elif path is not None:
            super().__init__(f"Error in {path}: {message}")
        else:
            super().__init__(message)


class HtmlParseError(Exception):
    """Raised when inline HTML is unsupported or unsafe."""

    def __init__(self, message: str, *, line: int | None = None, path: str | None = None) -> None:
        self.line = line
        self.path = path
        if line is not None and path is not None:
            super().__init__(f"Error in {path}:{line}: {message}")
        elif path is not None:
            super().__init__(f"Error in {path}: {message}")
        else:
            super().__init__(message)
