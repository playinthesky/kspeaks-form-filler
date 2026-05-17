from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class MasterConfig:
    """Thin wrapper around a master config until the schema stabilizes."""

    path: Path
    data: dict[str, Any]

    @property
    def parser_id(self) -> str:
        return str(self.data["parser"]["selected"])

    @property
    def templates_root(self) -> Path:
        root = self.data["paths"]["templates_root"]
        return (self.path.parent / root).resolve()


def load_master_config(path: str | Path) -> MasterConfig:
    config_path = Path(path).resolve()
    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a mapping in {config_path}")
    return MasterConfig(path=config_path, data=data)
