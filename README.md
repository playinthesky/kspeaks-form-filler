# kspeaks-form-filler

Korea Speaks form-filling skeleton for HWPX templates.

This public repository contains only code, schemas, documentation, generalized
slot skeletons, and placeholder examples. Real company data and original HWPX
forms live in a separate private repository.

## Phase 1 Scope

- `master.example.yaml`: placeholder project/form configuration.
- `schemas/master.schema.yaml`: schema for private `master.yaml` and public
  `master.example.yaml`.
- `typography.yaml`: default typography profile with 160% line spacing.
- `templates/forms/`: processed skeletons and slot maps.
- `docs/parser-selection_v0.1.0-alpha.md`: provisional parser review.
- `docs/data-source-plan_v0.1.0-alpha.md`: phased data source policy.
- `docs/output-format-plan_v0.1.0-alpha.md`: HWPX-only Phase 1 output policy.
- `docs/form-catalog_v0.1.0-alpha.md`: ten generalized form packages.
- `docs/skeleton-design-notes_v0.1.0-alpha.md`: first designed skeleton pass.
- `docs/google-docs-to-hwpx-flow-proposal_v0.1.0-alpha.md`: Google Docs
  source conversion proposal.
- `LICENSE`: MIT license for the public code repository.

## Current Parser Direction

`python-hwpx` is the provisional primary parser because this repository is
Python/YAML-first and needs direct package validation, template inspection, and
automation hooks. `kordoc` stays as a secondary candidate for form recognition,
Markdown conversion, and fallback tests once real HWPX files are available.

Final selection should wait until at least one real form is received and tested
with a three-value fill smoke test.

## Layout

```text
kspeaks-form-filler/
├── master.example.yaml
├── typography.yaml
├── schemas/
├── src/kspeaks_form_filler/
├── templates/forms/
├── docs/
└── scripts/
```

## Next Step

Keep the first original `source.hwpx` outside Git, then commit only the
slot-processed `templates/forms/<form_id>/skeleton/skeleton.hwpx` and
`templates/forms/<form_id>/mapping.json`.

Data source progression is fixed as: Phase 1 private `master.yaml` static
company information, Phase 2 form fixtures in YAML/JSON, Phase 4 Google Sheets
for settlement, deliverables, and staff information. CSV and database sources
are not adopted.

Form source progression now includes a likely Google Docs path: private Google
Docs source, Drive export to DOCX/HTML, normalized document model, HWPX
skeleton generation, then the existing slot-fill engine.

## Phase 1 Tools

```bash
kspeaks-form-filler validate-mapping templates/forms/project_proposal/mapping.json
kspeaks-form-filler list-slots --mapping templates/forms/project_proposal/mapping.json
kspeaks-form-filler fill \
  --skeleton templates/forms/project_proposal/skeleton/skeleton.hwpx \
  --mapping templates/forms/project_proposal/mapping.json \
  --values values.json \
  --output outputs/project_proposal.hwpx
```

The Phase 1 fill engine targets slot-processed HWPX skeletons and replaces
`{{slot_id}}` tokens inside text-based HWPX entries. It does not generate PDF
previews.

Designed skeleton packages are generated with:

```bash
python3 scripts/build_designed_skeletons.py
```

Private sample HWPX structure can be checked without printing document content:

```bash
python3 scripts/audit_hwpx_structure.py path/to/source.hwpx
```

The first designed skeleton pass covers `progress_brief`, `invoice`, and
`staff_profile`. These synthetic HWPX packages are public placeholder artifacts
for slot filling and smoke tests; final visual validation waits for private
source forms.

## Form Packages

- `project_proposal`
- `service_contract`
- `quotation`
- `invoice`
- `settlement_report`
- `staff_profile`
- `progress_brief`
- `nda`
- `self_construction_pledge`
- `integrity_pledge`

## Public/Private Split

```text
kspeaks-form-filler/                 # public, MIT
├── src/
├── docs/
├── schemas/
├── templates/forms/<id>/skeleton/
├── master.example.yaml
├── README.md
└── LICENSE

kspeaks-form-data/                   # private
├── master.yaml
├── templates/forms/<id>/source.hwpx
├── .seals/                          # local only, never cloud
└── audit_log/
```
