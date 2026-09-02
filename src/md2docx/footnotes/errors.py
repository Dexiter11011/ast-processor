"""Footnote-related errors."""


class FootnoteError(Exception):
    """Base class for footnote processing errors."""


class DuplicateFootnoteError(FootnoteError):
    def __init__(self, label: str) -> None:
        super().__init__(f"duplicate footnote definition: {label}")
        self.label = label


class MissingFootnoteError(FootnoteError):
    def __init__(self, label: str) -> None:
        super().__init__(f"undefined footnote: {label}")
        self.label = label
