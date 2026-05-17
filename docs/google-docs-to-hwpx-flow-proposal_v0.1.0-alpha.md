# Google Docs to HWPX Flow Proposal v0.1.0-alpha

## Context

Drive review changed the practical source assumption. Many Korea Speaks forms
appear to start as Google Docs, while Phase 1 assumed `source.hwpx` to
`skeleton.hwpx` to filled HWPX.

The output target stays HWPX. The source pipeline should expand to accept
Google Docs as a private source format.

## Reference Findings

- Google Drive API `files.export` exports a Google Workspace document to a
  requested MIME type and returns byte content, with a documented 10 MB export
  limit:
  https://developers.google.com/workspace/drive/api/reference/rest/v3/files/export
- Google Docs export formats include DOCX, ODT, RTF, PDF, plain text, HTML zip,
  EPUB, and Markdown. HWPX is not listed as a direct Google Docs export target:
  https://developers.google.com/workspace/drive/api/guides/ref-export-formats
- `public-doc-to-hwpx` shifted toward preserving form design and filling slots
  inside skeleton HWPX files, with scripts such as `fill_skeleton.py` and
  `make_skeleton.py`:
  https://github.com/Kminer2053/public-doc-to-hwpx

## Recommended Pipeline

```text
Private Google Docs source
  -> Drive export: DOCX and/or HTML zip
  -> document model normalization
  -> skeleton HWPX generation
  -> mapping.json slot map
  -> existing fill engine
  -> filled HWPX
```

## Integration Strategy

1. Keep Google Docs IDs, raw exports, and original forms in `kspeaks-form-data`.
2. Add a public converter layer later under `src/kspeaks_form_filler/converters/`.
3. Reuse `public-doc-to-hwpx` at the design-pattern level first:
   skeleton creation, slot filling, namespace cleanup, and validation checks.
4. If code is copied or adapted directly, keep the MIT notice and the existing
   credit in `LICENSE`.
5. Keep `mapping.json` as the stable contract between source conversion and
   HWPX filling.

## Local HWPX Sample Signal

Private sample HWPX files were checked for package structure only. The samples
showed real forms are style-heavy and table-heavy: standard `application/hwp+zip`
packages with 11-13 entries, one `Contents/section0.xml`, many `hh:charPr` /
`hh:paraPr` definitions, and up to 38 tables in one sampled document.

This makes a direct clean-room HWPX layout generator the wrong first production
move. The safer approach is:

1. obtain or create a source-derived skeleton,
2. preserve existing HWPX package structure and style IDs,
3. insert or replace only stable slot tokens,
4. run slot-fill and package validation,
5. defer visual/open validation to Hancom/한글 or a later rendering step.

## Proposed Components

- `GoogleDocsExporter`: exports private Google Docs to DOCX and HTML zip.
- `DocumentModel`: a neutral paragraph/table/style representation.
- `HwpxSkeletonBuilder`: writes generalized HWPX skeleton packages from the
  model.
- `SlotMapper`: produces or validates `mapping.json` against the skeleton.
- `HwpxRoundtripValidator`: checks package entries, slot coverage, and later
  Hancom/open validation.

## Format Choice

Use a two-export spike before locking the converter:

- DOCX export is likely better for table semantics and paragraph hierarchy.
- HTML zip export is likely better for CSS-like layout and embedded assets.

The first real Google Docs form should be exported both ways, then compared
against the current `progress_brief` design requirements.

## DOCX Conversion Spike

`scripts/convert_docx_to_hwpx.py` is a failed/experimental spike, not a usable
converter. It reads DOCX package XML directly and can extract paragraph/table
text, but it does not produce a trustworthy HWPX document for real use.

The current spike is intentionally text-first:

- preserves paragraph text,
- flattens each DOCX table row into a text row,
- writes `Preview/PrvText.txt`,
- writes a valid HWPX ZIP package structure,
- can reuse an existing renderable HWPX carrier via `--carrier-hwpx`,
- does not yet preserve Word visual styles, headers, footers, images, or true
  HWPX table objects.

Result of the local test: text extraction worked, but HWPX rendering fidelity
failed. This path must stay blocked behind `--allow-experimental` until a real
converter is implemented or an external converter such as LibreOffice/한글/한컴
tooling is available.

## Phase Impact

- Phase 1 remains valid: public schemas, mappings, and skeletons are still the
  core.
- Phase 2 should add fixtures for both HWPX-origin and Google-Docs-origin forms.
- Phase 3 should add visual/open validation after real forms exist.
- Phase 4 Google Sheets stays as the value source layer, not the form source
  layer.

## Decision

Adopt `Google Docs -> exported intermediate -> HWPX skeleton -> slot fill` as
the likely production path. Do not replace the current HWPX fill engine; put the
Google Docs work in front of it as a source-conversion step.

When an original HWPX source exists, use it directly as the skeleton source.
When the source exists only in Google Docs, convert it once into a style-preserved
HWPX skeleton, then treat it the same way as native HWPX templates.
