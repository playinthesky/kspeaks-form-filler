from __future__ import annotations

import json
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from kspeaks_form_filler.engine import fill_hwpx_template
from kspeaks_form_filler.slots import iter_slots, load_mapping, validate_mapping


FORM_IDS = [
    "project_proposal",
    "service_contract",
    "quotation",
    "invoice",
    "settlement_report",
    "staff_profile",
    "progress_brief",
    "nda",
    "self_construction_pledge",
    "integrity_pledge",
]

FORM_KO_NAMES = {
    "project_proposal": "사업제안서",
    "service_contract": "용역계약서",
    "quotation": "견적서",
    "invoice": "청구서",
    "settlement_report": "정산보고",
    "staff_profile": "직원정보",
    "progress_brief": "중간보고",
    "nda": "비밀유지 서약서",
    "self_construction_pledge": "자체시공 서약서",
    "integrity_pledge": "청렴 서약서",
}

DESIGNED_SKELETON_IDS = [
    "progress_brief",
    "invoice",
    "staff_profile",
]

SKELETON_REQUIRED_ENTRIES = {
    "mimetype",
    "version.xml",
    "Contents/content.hpf",
    "Contents/header.xml",
    "Contents/section0.xml",
    "Preview/PrvText.txt",
    "settings.xml",
    "META-INF/container.xml",
    "META-INF/container.rdf",
    "META-INF/manifest.xml",
}

TEXT_ENTRY_SUFFIXES = (".xml", ".txt")

REQUIRED_PATHS = [
    "master.example.yaml",
    "typography.yaml",
    "schemas/master.schema.yaml",
    "templates/forms/README.md",
    *[f"templates/forms/{form_id}/manifest.yaml" for form_id in FORM_IDS],
    *[f"templates/forms/{form_id}/mapping.json" for form_id in FORM_IDS],
    "src/kspeaks_form_filler/parsers/base.py",
    "src/kspeaks_form_filler/engine.py",
    "src/kspeaks_form_filler/slots.py",
    "src/kspeaks_form_filler/cli.py",
    "docs/parser-selection_v0.1.0-alpha.md",
    "docs/source-storage-policy_v0.1.0-alpha.md",
    "docs/data-source-plan_v0.1.0-alpha.md",
    "docs/output-format-plan_v0.1.0-alpha.md",
    "docs/form-catalog_v0.1.0-alpha.md",
    "docs/skeleton-design-notes_v0.1.0-alpha.md",
    "docs/google-docs-to-hwpx-flow-proposal_v0.1.0-alpha.md",
    "scripts/build_designed_skeletons.py",
    "scripts/audit_hwpx_structure.py",
    *[
        f"templates/forms/{form_id}/skeleton/skeleton.hwpx"
        for form_id in DESIGNED_SKELETON_IDS
    ],
    "LICENSE",
]


def main() -> int:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    typography = (ROOT / "typography.yaml").read_text(encoding="utf-8")
    master = (ROOT / "master.example.yaml").read_text(encoding="utf-8")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    mapping_paths = sorted((ROOT / "templates/forms").glob("*/mapping.json"))
    mapping_warnings = []
    for mapping_path in mapping_paths:
        mapping_warnings.extend(validate_mapping(load_mapping(mapping_path)))

    skeleton_warnings = _validate_designed_skeletons()
    smoke_ok = _run_fill_smoke_test()

    checks = {
        "required_paths": not missing,
        "line_spacing_160": "value: 160" in typography and "type: PERCENT" in typography,
        "parser_selected": "selected: python_hwpx" in master,
        "phase1_master_only": "source: master.yaml" in master
        and "purpose: static_company_info" in master,
        "example_config_placeholder": "코리아스픽스" not in master
        and "owner: Korea Speaks" not in master,
        "phase1_hwpx_only": "formats:" in master
        and "- hwpx" in master
        and "pdf_preview: excluded" in master,
        "phase2_fixtures": "source: form_fixtures" in master
        and "purpose: test_data" in master,
        "phase4_google_sheets": "source: google_sheets" in master
        and "settlement" in master
        and "deliverables" in master
        and "staff_info" in master,
        "csv_db_rejected": "source: csv" in master and "source: database" in master,
        "no_phase1_data_input": "data/input.yaml" not in master and "data_sources:" not in master,
        "ten_forms": all(form_id in master for form_id in FORM_IDS),
        "source_external": ("commit_to_public_git: false" in master)
        and ("canonical_filename: source.hwpx" in master)
        and ("path: templates/forms/project_proposal/source.hwpx" in master),
        "mapping_committed": "mapping: templates/forms/project_proposal/mapping.json" in master,
        "ten_mapping_files": len(mapping_paths) == 10,
        "ko_names_present": all(
            f'"ko_name": "{ko_name}"'
            in (ROOT / f"templates/forms/{form_id}/mapping.json").read_text(encoding="utf-8")
            for form_id, ko_name in FORM_KO_NAMES.items()
        ),
        "mapping_valid": not mapping_warnings,
        "designed_skeletons": not skeleton_warnings,
        "fill_engine_smoke": smoke_ok,
        "real_master_ignored": "master.yaml" in gitignore,
        "forms_root": (ROOT / "templates/forms").is_dir(),
    }

    for name, passed in checks.items():
        print(f"{name}: {'ok' if passed else 'fail'}")

    if missing:
        print("missing:")
        for path in missing:
            print(f"  - {path}")
    if mapping_warnings:
        print("mapping warnings:")
        for warning in mapping_warnings:
            print(f"  - {warning}")
    if skeleton_warnings:
        print("skeleton warnings:")
        for warning in skeleton_warnings:
            print(f"  - {warning}")

    return 0 if all(checks.values()) else 1


def _validate_designed_skeletons() -> list[str]:
    warnings = []
    for form_id in DESIGNED_SKELETON_IDS:
        skeleton_path = ROOT / "templates" / "forms" / form_id / "skeleton" / "skeleton.hwpx"
        mapping_path = ROOT / "templates" / "forms" / form_id / "mapping.json"
        if not skeleton_path.exists():
            warnings.append(f"{form_id}: missing skeleton.hwpx")
            continue
        try:
            with zipfile.ZipFile(skeleton_path, "r") as archive:
                names = archive.namelist()
                entry_set = set(names)
                missing_entries = sorted(SKELETON_REQUIRED_ENTRIES.difference(entry_set))
                if missing_entries:
                    warnings.append(f"{form_id}: missing entries {', '.join(missing_entries)}")
                if not names or names[0] != "mimetype":
                    warnings.append(f"{form_id}: mimetype is not the first zip entry")
                if archive.read("mimetype").decode("utf-8") != "application/hwp+zip":
                    warnings.append(f"{form_id}: invalid mimetype")
                text_entries = []
                for name in names:
                    if name.endswith(TEXT_ENTRY_SUFFIXES):
                        text_entries.append(archive.read(name).decode("utf-8"))
        except (zipfile.BadZipFile, UnicodeDecodeError) as exc:
            warnings.append(f"{form_id}: invalid HWPX package: {exc}")
            continue

        text_blob = "\n".join(text_entries)
        mapping = load_mapping(mapping_path)
        for slot in iter_slots(mapping):
            if slot.token not in text_blob:
                warnings.append(f"{form_id}: missing token {slot.token}")
        if form_id == "progress_brief":
            markers = ("[HEADER_BOX", "[KEY_SUMMARY_BOX", "[TWO_COLUMN_TABLE", "#004D80", "#EF8009")
            for marker in markers:
                if marker not in text_blob:
                    warnings.append(f"{form_id}: missing design marker {marker}")
    return warnings


def _run_fill_smoke_test() -> bool:
    mapping = {
        "slots": [
            {
                "id": "project_name",
                "label": "Project name",
                "required": True,
                "value_type": "text",
                "target": {"strategy": "placeholder_token", "token": "{{project_name}}"},
            }
        ]
    }
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source = temp_path / "source.hwpx"
        output = temp_path / "output.hwpx"
        with zipfile.ZipFile(source, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("Contents/section0.xml", "<p>{{project_name}}</p>")
        report = fill_hwpx_template(source, output, mapping, {"project_name": "Example"})
        if report.applied_count != 1:
            return False
        with zipfile.ZipFile(output, "r") as archive:
            text = archive.read("Contents/section0.xml").decode("utf-8")
        return "Example" in text and "{{project_name}}" not in text


if __name__ == "__main__":
    raise SystemExit(main())
