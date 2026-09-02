"""DOCX package validation errors."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ValidationIssue:
    category: str
    message: str
    part: str = ""
    severity: str = "error"


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)

    def add(self, category: str, message: str, *, part: str = "", severity: str = "error") -> None:
        self.issues.append(
            ValidationIssue(category=category, message=message, part=part, severity=severity)
        )

    def merge(self, other: ValidationReport) -> None:
        self.issues.extend(other.issues)

    def format_messages(self) -> str:
        lines = []
        for issue in self.issues:
            prefix = f"[{issue.category}]"
            if issue.part:
                prefix += f" {issue.part}:"
            lines.append(f"{prefix} {issue.message}")
        return "\n".join(lines)

    def raise_if_errors(self) -> None:
        if self.ok:
            return
        raise DocxValidationError(self.format_messages())


class DocxValidationError(Exception):
    """Raised when DOCX package validation fails."""
