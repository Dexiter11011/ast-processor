"""Load external YAML document themes."""

from __future__ import annotations

from pathlib import Path

import yaml

from md2docx.styles.theme import DocumentTheme
from md2docx.themes.errors import ThemeLoadError, ThemeValidationError
from md2docx.themes.schema import parse_theme_data
from md2docx.themes.yaml_theme import YamlDocumentTheme


class ThemeLoader:
    """Read, validate, and convert external YAML themes into DocumentTheme instances."""

    @staticmethod
    def load(path: Path) -> DocumentTheme:
        if not path.is_file():
            raise ThemeLoadError(f"theme file not found: {path}")

        raw_text = path.read_text(encoding="utf-8")
        if not raw_text.strip():
            raise ThemeLoadError(f"theme file is empty: {path}")

        try:
            data = yaml.safe_load(raw_text)
        except yaml.YAMLError as exc:
            problem = exc.problem_mark
            if problem is not None:
                raise ThemeLoadError(
                    f"invalid theme YAML: line {problem.line + 1}, column {problem.column + 1}"
                ) from exc
            raise ThemeLoadError("invalid theme YAML") from exc

        try:
            name, tokens = parse_theme_data(data)
        except ThemeValidationError as exc:
            if exc.path:
                raise ThemeValidationError(exc.path, exc.message) from exc
            raise

        return YamlDocumentTheme(name=name, tokens=tokens)
