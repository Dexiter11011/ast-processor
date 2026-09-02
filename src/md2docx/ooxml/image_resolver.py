"""Image path resolution."""

from __future__ import annotations

from pathlib import Path

from md2docx.processor.errors import ImagePathError


def resolve_image_path(src: str, base_dir: Path) -> Path:
    """Resolve *src* relative to *base_dir*; reject paths outside the source tree."""
    path = Path(src)
    base_resolved = base_dir.resolve()
    if path.is_absolute():
        resolved = path.resolve()
    else:
        resolved = (base_resolved / path).resolve()
    try:
        resolved.relative_to(base_resolved)
    except ValueError as exc:
        raise ImagePathError(src) from exc
    return resolved
