from dataclasses import dataclass, field
from decimal import Decimal

from pilot_framework.mappings import TableMapping


@dataclass
class ReconciliationResult:
    table: str
    source_rows: int
    target_rows: int
    missing_in_target: list = field(default_factory=list)
    extra_in_target: list = field(default_factory=list)
    mismatches: list = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not (self.missing_in_target or self.extra_in_target or self.mismatches)

    def summary(self, limit: int = 10) -> str:
        lines = [
            f"{self.table}: source={self.source_rows} target={self.target_rows} "
            f"missing={len(self.missing_in_target)} extra={len(self.extra_in_target)} "
            f"mismatched_values={len(self.mismatches)}"
        ]
        if self.missing_in_target:
            lines.append(f"  missing keys: {self.missing_in_target[:limit]}")
        if self.extra_in_target:
            lines.append(f"  extra keys: {self.extra_in_target[:limit]}")
        for m in self.mismatches[:limit]:
            lines.append(
                f"  key={m['key']} {m['column']}: source={m['expected']!r} target={m['actual']!r}"
            )
        return "\n".join(lines)


def normalise(value):
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, float):
        return Decimal(str(value))
    return value


def reconcile(
    mapping: TableMapping, source_rows: list[dict], target_rows: list[dict]
) -> ReconciliationResult:
    """Compare source rows to target rows key by key, applying column mapping and transforms."""
    source_by_key = {r[mapping.source_key]: r for r in source_rows}
    target_by_key = {r[mapping.target_key]: r for r in target_rows}
    result = ReconciliationResult(
        table=mapping.name, source_rows=len(source_rows), target_rows=len(target_rows)
    )
    result.missing_in_target = sorted(source_by_key.keys() - target_by_key.keys())
    result.extra_in_target = sorted(target_by_key.keys() - source_by_key.keys())
    for key in sorted(source_by_key.keys() & target_by_key.keys()):
        src, tgt = source_by_key[key], target_by_key[key]
        for col in mapping.columns:
            raw = src[col.source]
            expected = normalise(col.transform.get(raw, raw) if col.transform else raw)
            actual = normalise(tgt[col.target])
            if expected != actual:
                result.mismatches.append(
                    {"key": key, "column": col.target, "expected": expected, "actual": actual}
                )
    return result
