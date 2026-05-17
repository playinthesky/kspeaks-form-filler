from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

from .engine import fill_hwpx_template
from .slots import extract_tokens, iter_slots, load_mapping, validate_mapping


def _load_values(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    else:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("Install PyYAML or use JSON values for this command.") from exc
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
    if not isinstance(data, dict):
        raise ValueError(f"Expected key-value data in {path}")
    return data


def _tokens_from_hwpx(path: Path) -> set[str]:
    tokens: set[str] = set()
    with zipfile.ZipFile(path, "r") as archive:
        for name in archive.namelist():
            if not name.endswith((".xml", ".rels", ".txt")):
                continue
            try:
                text = archive.read(name).decode("utf-8")
            except UnicodeDecodeError:
                continue
            tokens.update(extract_tokens(text))
    return tokens


def _cmd_validate_mapping(args: argparse.Namespace) -> int:
    mapping = load_mapping(args.mapping)
    warnings = validate_mapping(mapping)
    for slot in iter_slots(mapping):
        required = "required" if slot.required else "optional"
        print(f"{slot.id}\t{required}\t{slot.token}")
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    return 0


def _cmd_list_slots(args: argparse.Namespace) -> int:
    if args.skeleton:
        for token in sorted(_tokens_from_hwpx(args.skeleton)):
            print(token)
        return 0

    mapping = load_mapping(args.mapping)
    for slot in iter_slots(mapping):
        print(slot.id)
    return 0


def _cmd_fill(args: argparse.Namespace) -> int:
    mapping = load_mapping(args.mapping)
    values = _load_values(args.values)
    report = fill_hwpx_template(args.skeleton, args.output, mapping, values)
    print(f"applied_count={report.applied_count}")
    if report.unused_values:
        print("unused_values=" + ",".join(report.unused_values))
    for warning in report.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kspeaks-form-filler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_mapping = subparsers.add_parser("validate-mapping")
    validate_mapping.add_argument("mapping", type=Path)
    validate_mapping.set_defaults(func=_cmd_validate_mapping)

    list_slots = subparsers.add_parser("list-slots")
    list_slots.add_argument("--mapping", type=Path)
    list_slots.add_argument("--skeleton", type=Path)
    list_slots.set_defaults(func=_cmd_list_slots)

    fill = subparsers.add_parser("fill")
    fill.add_argument("--skeleton", required=True, type=Path)
    fill.add_argument("--mapping", required=True, type=Path)
    fill.add_argument("--values", required=True, type=Path)
    fill.add_argument("--output", required=True, type=Path)
    fill.set_defaults(func=_cmd_fill)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "list-slots" and not (args.mapping or args.skeleton):
        parser.error("list-slots requires --mapping or --skeleton")
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
