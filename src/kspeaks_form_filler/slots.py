from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SLOT_TOKEN_RE = re.compile(r"\{\{([a-zA-Z][a-zA-Z0-9_\-]*)\}\}")


@dataclass(frozen=True)
class Slot:
    id: str
    label: str
    required: bool
    value_type: str
    token: str


def load_mapping(path: str | Path) -> dict[str, Any]:
    mapping_path = Path(path)
    with mapping_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {mapping_path}")
    return data


def iter_slots(mapping: dict[str, Any]) -> list[Slot]:
    raw_slots = mapping.get("slots", [])
    if not isinstance(raw_slots, list):
        raise ValueError("mapping.json must contain a list under `slots`")

    slots: list[Slot] = []
    seen: set[str] = set()
    for raw_slot in raw_slots:
        if not isinstance(raw_slot, dict):
            raise ValueError("Each slot must be a JSON object")
        slot_id = str(raw_slot["id"])
        if slot_id in seen:
            raise ValueError(f"Duplicate slot id: {slot_id}")
        seen.add(slot_id)

        target = raw_slot.get("target", {})
        if not isinstance(target, dict):
            raise ValueError(f"Slot {slot_id} target must be a JSON object")
        token = str(target.get("token") or f"{{{{{slot_id}}}}}")

        slots.append(
            Slot(
                id=slot_id,
                label=str(raw_slot.get("label", slot_id)),
                required=bool(raw_slot.get("required", False)),
                value_type=str(raw_slot.get("value_type", "text")),
                token=token,
            )
        )
    return slots


def required_slot_ids(mapping: dict[str, Any]) -> set[str]:
    return {slot.id for slot in iter_slots(mapping) if slot.required}


def extract_tokens(text: str) -> set[str]:
    return {match.group(1) for match in SLOT_TOKEN_RE.finditer(text)}


def validate_mapping(mapping: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if not mapping.get("form_id"):
        warnings.append("mapping.json is missing form_id")
    if not mapping.get("ko_name"):
        warnings.append("mapping.json is missing ko_name")
    slots = iter_slots(mapping)
    if not slots:
        warnings.append("mapping.json has no slots")
    for slot in slots:
        if not slot.token.startswith("{{") or not slot.token.endswith("}}"):
            warnings.append(f"Slot {slot.id} uses a nonstandard token: {slot.token}")
    return warnings
