# Data Source Plan v0.1.0-alpha

## Adopted

| Phase | Data source | Scope |
|---|---|---|
| Phase 1 | Private `master.yaml` only | Static company information. Public repo has `master.example.yaml` placeholders only. |
| Phase 2 | Form-specific fixtures YAML/JSON | Test data for each form package. |
| Phase 4 | Google Sheets | Settlement, deliverables, and staff information. |

## Not Adopted

| Source | Reason |
|---|---|
| CSV | Google Sheets is the higher-level operational source. |
| Database | Too heavy for the current form-filling scope. |

## Repository Implication

- Do not add a generic `data/input.yaml` path in Phase 1.
- Do not commit real `master.yaml` to the public repository.
- Keep Phase 2 fixture files under each form package, for example
  `templates/forms/<form_id>/fixtures/*.yaml` or `*.json`.
- Keep Google Sheets connector work out of Phase 1 and reserve it for Phase 4.
