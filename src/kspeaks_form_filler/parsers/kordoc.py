from __future__ import annotations

from pathlib import Path

from .base import FilledDocument, TemplateInspection


class KordocParser:
    parser_id = "kordoc"

    def __init__(self, executable: str = "npx") -> None:
        self.executable = executable

    def inspect_template(self, source: Path) -> TemplateInspection:
        raise NotImplementedError(
            "Kordoc is a Phase 2 fallback candidate. Verify its local CLI/API shape before enabling."
        )

    def fill_template(self, source: Path, output: Path, values: dict[str, str]) -> FilledDocument:
        raise NotImplementedError(
            "Kordoc is a Phase 2 fallback candidate. Verify its local CLI/API shape before enabling."
        )
