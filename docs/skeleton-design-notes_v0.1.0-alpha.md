# Skeleton Design Notes v0.1.0-alpha

This note records the first public, generalized skeleton design pass for three
high-use forms.

## Scope

- `progress_brief`: strengthened as the priority Korea Speaks progress brief.
- `invoice`: strengthened as a clean financial request skeleton.
- `staff_profile`: strengthened as an internal staff information skeleton.

The committed `skeleton.hwpx` files are generalized public artifacts. They do
not contain real company data, original customer forms, seals, account numbers,
or source Google Docs/HWPX files.

## Design Tokens

- Primary navy: `#004D80`
- Accent orange: `#EF8009`
- Light navy fill: `#E8F1F7`
- Light orange fill: `#FFF3E8`
- Default line spacing: `160%`

## Form Treatments

### `progress_brief`

Applied the signature Korea Speaks report layout:

- header box
- key summary box
- two-column table structure
- metadata row for project, period, date, and preparer
- public placeholder tokens only

### `invoice`

Applied a restrained invoice layout:

- header box
- billing summary box
- amount table
- private-data note for account, seal, and real company values

### `staff_profile`

Applied an internal profile-card layout:

- header box
- two-column basic/settlement information table
- operational note box
- private-data note for sensitive account values

## Limitation

These are synthetic HWPX packages generated before receiving real source forms.
They support slot-fill smoke tests and public repository review. Final visual
roundtrip validation in Hancom/한글 should happen after the private source forms
are collected.

## Sample HWPX Check

Local sample files were checked for structure only; no source content is
committed. The samples were standard `application/hwp+zip` packages with one
section file and rich style/table structure:

- 11-13 package entries
- 36-302 paragraph style definitions
- 12-123 border/fill definitions
- 2-38 tables per document
- up to 538 table cells in the largest sampled form

This confirms the production path should preserve real source skeletons instead
of generating visual HWPX from scratch. The designed skeletons in this public
repository remain placeholders for slot coverage and automation tests.
