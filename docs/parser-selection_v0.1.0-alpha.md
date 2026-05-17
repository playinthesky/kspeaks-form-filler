# HWPX Parser Selection v0.1.0-alpha

Status: provisional until real HWPX form templates arrive.

## Decision

Use `python-hwpx` as the provisional primary backend and keep `kordoc` as a
secondary evaluation/fallback backend.

This keeps Phase 1 Python/YAML-first while preserving an escape hatch if a real
form requires Kordoc's broader document parser or form-recognition path.

## Candidate Review

| Candidate | Fit | Risk | Phase 1 Position |
|---|---|---|---|
| `python-hwpx` | Pure Python HWPX read/edit/generate/validate, direct fit for this repo's Python config and tests. | Requires Python 3.10+. Public package marks the project as alpha, so real-template validation is mandatory. | Provisional primary. |
| `kordoc` | Broad Korean-document parser: HWP/HWPX/PDF/XLSX/DOCX to Markdown, Markdown to HWPX, and form filling. Strong for ingestion and fallback. | Node/npm runtime boundary; CLI/API shape must be verified locally before making it the core backend. | Secondary candidate and fallback; code adapter is intentionally placeholder-only in Phase 1. |

## Reference Repo Takeaways

`public-doc-to-hwpx` is useful less as a dependency and more as an architecture
reference:

- Preserve the public-document template and fill content into slots.
- Keep form-specific slot mappings next to each template.
- Add validation and post-processing hooks rather than assuming generated XML is
  always accepted by Hancom.
- Treat page/layout behavior as a regression-test surface.

## Final Selection Gate

When the first original HWPX arrives:

1. Inspect fields with `python-hwpx`.
2. Inspect the same file with `kordoc`.
3. Fill three representative fields: title, body text, date or name.
4. Open the output in Hancom Office on macOS.
5. Confirm table borders, line spacing, cell alignment, and page layout stayed stable.
6. Keep the backend that passes with the least custom patching.

## Sources Checked

- https://github.com/Kminer2053/public-doc-to-hwpx
- https://github.com/airmang/python-hwpx
- https://pypi.org/project/python-hwpx/
- https://github.com/chrisryugj/kordoc
