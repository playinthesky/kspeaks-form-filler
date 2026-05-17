from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


class ParserDependencyError(RuntimeError):
    """Raised when an optional parser backend is not installed."""


@dataclass(frozen=True)
class TemplateInspection:
    parser_id: str
    source: Path
    slots: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FilledDocument:
    parser_id: str
    source: Path
    output: Path
    applied_count: int
    failed_fields: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class HwpxParser(Protocol):
    parser_id: str

    def inspect_template(self, source: Path) -> TemplateInspection:
        """Inspect an HWPX template and return known or inferred slots."""

    def fill_template(self, source: Path, output: Path, values: dict[str, str]) -> FilledDocument:
        """Fill mapped values into an HWPX template."""
