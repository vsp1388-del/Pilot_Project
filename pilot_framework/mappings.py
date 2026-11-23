from dataclasses import dataclass, field
from pathlib import Path

import yaml

from pilot_framework.config import PROJECT_ROOT

DEFAULT_MAPPINGS = PROJECT_ROOT / "config" / "mappings.yaml"


@dataclass(frozen=True)
class ColumnMapping:
    source: str
    target: str
    transform: dict = field(default_factory=dict)


@dataclass(frozen=True)
class TableMapping:
    name: str
    source_table: str
    target_table: str
    source_key: str
    target_key: str
    columns: tuple[ColumnMapping, ...]


def _column(source: str, spec) -> ColumnMapping:
    if isinstance(spec, str):
        return ColumnMapping(source=source, target=spec)
    return ColumnMapping(source=source, target=spec["target"], transform=spec.get("transform", {}))


def load_mappings(path: str | Path = DEFAULT_MAPPINGS) -> dict[str, TableMapping]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    mappings = {}
    for name, spec in data["tables"].items():
        mappings[name] = TableMapping(
            name=name,
            source_table=spec["source_table"],
            target_table=spec["target_table"],
            source_key=spec["key"]["source"],
            target_key=spec["key"]["target"],
            columns=tuple(_column(src, tgt) for src, tgt in spec["columns"].items()),
        )
    return mappings
