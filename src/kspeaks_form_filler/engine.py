from __future__ import annotations

import html
import shutil
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .slots import iter_slots, required_slot_ids


TEXT_ENTRY_SUFFIXES = (".xml", ".rels", ".txt")


@dataclass(frozen=True)
class FillReport:
    source: Path
    output: Path
    applied_count: int
    missing_required: list[str] = field(default_factory=list)
    unused_values: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_values(mapping: dict[str, Any], values: dict[str, Any]) -> tuple[list[str], list[str]]:
    required = required_slot_ids(mapping)
    missing = sorted(slot_id for slot_id in required if slot_id not in values or values[slot_id] in (None, ""))
    known = {slot.id for slot in iter_slots(mapping)}
    unused = sorted(key for key in values if key not in known)
    return missing, unused


def fill_hwpx_template(
    source: str | Path,
    output: str | Path,
    mapping: dict[str, Any],
    values: dict[str, Any],
    *,
    fail_on_missing_required: bool = True,
) -> FillReport:
    source_path = Path(source)
    output_path = Path(output)
    missing, unused = validate_values(mapping, values)
    if missing and fail_on_missing_required:
        raise ValueError(f"Missing required values: {', '.join(missing)}")

    if not source_path.exists():
        raise FileNotFoundError(source_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    replacements = {
        slot.token: html.escape(str(values[slot.id]), quote=True)
        for slot in iter_slots(mapping)
        if slot.id in values and values[slot.id] is not None
    }

    applied_count = 0
    with zipfile.ZipFile(source_path, "r") as zin:
        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                raw = zin.read(info.filename)
                if info.filename.endswith(TEXT_ENTRY_SUFFIXES):
                    try:
                        text = raw.decode("utf-8")
                    except UnicodeDecodeError:
                        zout.writestr(info, raw)
                        continue
                    for token, value in replacements.items():
                        count = text.count(token)
                        if count:
                            applied_count += count
                            text = text.replace(token, value)
                    zout.writestr(info, text.encode("utf-8"))
                else:
                    zout.writestr(info, raw)

    warnings = []
    if not applied_count:
        warnings.append("No slot tokens were replaced")

    return FillReport(
        source=source_path,
        output=output_path,
        applied_count=applied_count,
        missing_required=missing,
        unused_values=unused,
        warnings=warnings,
    )


def copy_skeleton(source: str | Path, output: str | Path) -> None:
    source_path = Path(source)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, output_path)
