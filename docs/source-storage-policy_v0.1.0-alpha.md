# Source Storage Policy v0.1.0-alpha

## Decision

Original form files named `source.hwpx` stay outside the public Git repository.

Allowed storage:

- `kspeaks-form-data` private repository.

Committed artifacts:

- `skeleton.hwpx`: OK to commit after slotting, because it is a Korea Speaks
  processed company artifact.
- `mapping.json`: OK to commit as the canonical slot map.

## Repository Rules

- Do not commit original `source.hwpx` to `kspeaks-form-filler`.
- Do not commit files under `templates/forms/**/raw/*.hwpx`.
- Do not commit real `master.yaml` to `kspeaks-form-filler`.
- Do not sync `.seals/` to any cloud service.
- Keep source location metadata in each form's `manifest.yaml`.
- Keep the slot map next to the skeleton as `mapping.json`.

## Rationale

This protects third-party or client-provided source forms while keeping the
operational assets needed for repeatable form filling in Git.
