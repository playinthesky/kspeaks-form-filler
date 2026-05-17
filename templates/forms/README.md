# templates/forms

Each form gets its own directory so generated skeletons and slot maps stay
together. Original `source.hwpx` files stay outside Git.

```text
templates/forms/<form_id>/
├── manifest.yaml
├── mapping.json
├── skeleton/
│   └── skeleton.hwpx
└── notes.md
```

Rules:

- Preserve the original HWPX layout unless a change is explicitly approved.
- Put every fillable field in `mapping.json`.
- Keep raw source filenames visible in `manifest.yaml`.
- Add a smoke-test fixture before marking a form ready.
- Never commit original `source.hwpx`; store it in `kspeaks-form-data`.
- Add fixture YAML/JSON only from Phase 2 onward.
