from __future__ import annotations

from pathlib import Path

from .base import FilledDocument, ParserDependencyError, TemplateInspection


class PythonHwpxParser:
    parser_id = "python_hwpx"

    def _document_class(self):
        try:
            from hwpx import HwpxDocument
        except ImportError as exc:
            raise ParserDependencyError(
                "Install the optional HWPX backend with `pip install .[hwpx]`."
            ) from exc
        return HwpxDocument

    def inspect_template(self, source: Path) -> TemplateInspection:
        hwpx_document = self._document_class()
        document = hwpx_document.open(str(source))
        text = document.export_markdown()
        slots = sorted({token for token in text.split() if token.startswith("{{") and token.endswith("}}")})
        return TemplateInspection(parser_id=self.parser_id, source=source, slots=slots)

    def fill_template(self, source: Path, output: Path, values: dict[str, str]) -> FilledDocument:
        hwpx_document = self._document_class()
        document = hwpx_document.open(str(source))
        result = document.fill_by_path(values)
        document.save_to_path(output)
        return FilledDocument(
            parser_id=self.parser_id,
            source=source,
            output=output,
            applied_count=int(result.get("applied_count", 0)),
            failed_fields=list(result.get("failed", [])),
        )
