# Phase 1 Status v0.1.0-alpha

Date: 2026-05-17
Repo: `kspeaks-form-filler`

## Completed

- Created the repository skeleton under `/Users/inthesky/code/kspeaks-form-filler`.
- Marked `kspeaks-form-filler` as the public MIT code repository.
- Replaced real `master.yaml` with placeholder-only `master.example.yaml`.
- Documented the `kspeaks-form-data` private-data repository boundary; source
  collection and final private repo setup are deferred until office return.
- Added `.python-version` and `pyproject.toml`; project runtime is Python 3.10+
  because `python-hwpx` requires it.
- Added `master.example.yaml` and `schemas/master.schema.yaml`.
- Added `typography.yaml` with default 160% line spacing.
- Added `templates/forms/` structure for six generalized form packages.
- Reflected source-file policy: original `source.hwpx` stays external; processed
  `skeleton.hwpx` and `mapping.json` are Git-committable.
- Reflected data-source phasing: Phase 1 uses private `master.yaml` static
  company info; public repo keeps only `master.example.yaml`; Phase 2 adds form
  fixtures YAML/JSON; Phase 4 adds Google Sheets.
- Marked CSV and database sources as not adopted.
- Reflected output policy: Phase 1 outputs HWPX only; PDF preview is deferred to
  Phase 2 or Phase 3 review.
- Added ten generalized form packages: `project_proposal`, `service_contract`,
  `quotation`, `invoice`, `settlement_report`, `staff_profile`,
  `progress_brief`, `nda`, `self_construction_pledge`, `integrity_pledge`.
- Added `ko_name` aliases to every `mapping.json`.
- Added Phase 1 slot tools and a token-based HWPX fill engine.
- Added parser adapter boundaries for `python-hwpx` and `kordoc`; the `kordoc`
  adapter is placeholder-only until its local CLI/API shape is verified.
- Added parser-selection memo with provisional decision.
- Added a Phase 1 validation script.

## Provisional Technical Direction

- Primary backend: `python-hwpx`.
- Secondary backend: `kordoc`.
- Final backend selection waits for the first real HWPX form and a smoke test.

## Deferred

- Private data repository final setup.
- First original `source.hwpx` collection.
- PDF preview decision in Phase 2 or Phase 3.

## Not Blocked

No source HWPX file is needed for the Phase 1 skeleton. The next meaningful
engineering step starts when one clean original form arrives.
