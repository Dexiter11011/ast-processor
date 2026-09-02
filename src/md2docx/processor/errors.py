"""Processor errors."""


class UnsupportedNodeError(Exception):
    """Raised when no handler is registered for an AST node type."""

    def __init__(self, node_type: str) -> None:
        self.node_type = node_type
        super().__init__(f"unsupported AST node: {node_type}")


class ImageNotFoundError(Exception):
    """Raised when a Markdown image references a missing file."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"image not found: {path}")


class ImagePathError(Exception):
    """Raised when an image path escapes the allowed source directory."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"image path not allowed: {path}")


class TemplateModeError(Exception):
    """Raised when Markdown features are incompatible with DOCX templates."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
