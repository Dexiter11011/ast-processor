"""Load existing DOCX files as template packages."""

from __future__ import annotations

import zipfile
from pathlib import Path, PurePosixPath

from md2docx.templates.errors import TemplateLoadError
from md2docx.templates.package import REQUIRED_TEMPLATE_PARTS, TemplatePackage


def _validate_part_name(name: str) -> None:
    if name.startswith("/") or "\\" in name:
        raise TemplateLoadError(f"invalid template entry path: {name}")
    path = PurePosixPath(name)
    if ".." in path.parts:
        raise TemplateLoadError(f"invalid template entry path: {name}")


class DocxPackageReader:
    """Read an existing DOCX package into a TemplatePackage."""

    @staticmethod
    def load(path: Path) -> TemplatePackage:
        if not path.is_file():
            raise TemplateLoadError(f"template file not found: {path}")

        try:
            with zipfile.ZipFile(path, "r") as zf:
                bad = zf.testzip()
                if bad is not None:
                    raise TemplateLoadError(f"invalid DOCX template: corrupt ZIP entry: {bad}")
                parts: dict[str, bytes] = {}
                for name in zf.namelist():
                    _validate_part_name(name)
                    parts[name] = zf.read(name)
        except zipfile.BadZipFile as exc:
            raise TemplateLoadError(f"invalid DOCX template: not a ZIP archive: {path}") from exc
        except OSError as exc:
            raise TemplateLoadError(f"cannot read template file: {path}") from exc

        missing = [part for part in REQUIRED_TEMPLATE_PARTS if part not in parts]
        if missing:
            joined = ", ".join(missing)
            raise TemplateLoadError(f"invalid DOCX template: missing required part(s): {joined}")

        return TemplatePackage(parts=parts)
