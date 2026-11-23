import csv
from dataclasses import dataclass
from pathlib import Path

from openpyxl import load_workbook

REQUIRED_COLUMNS = ("rule_id", "description", "database", "sql", "expected")


@dataclass(frozen=True)
class Rule:
    rule_id: str
    description: str
    database: str
    sql: str
    expected: str
    severity: str = "High"
    enabled: bool = True


def _header_key(value) -> str:
    return str(value or "").strip().lower().replace(" ", "_")


def _to_rule(row: dict) -> Rule:
    missing = [c for c in REQUIRED_COLUMNS if row.get(c) is None or not str(row[c]).strip()]
    if missing:
        raise ValueError(f"Rule row {row} is missing {missing}")
    database = str(row["database"]).strip().lower()
    if database not in ("source", "target"):
        raise ValueError(f"Rule {row['rule_id']}: database must be source or target")
    enabled = str(row.get("enabled", "Y") or "Y").strip().upper() not in ("N", "NO", "FALSE")
    return Rule(
        rule_id=str(row["rule_id"]).strip(),
        description=str(row["description"]).strip(),
        database=database,
        sql=str(row["sql"]).strip(),
        expected=str(row["expected"]).strip(),
        severity=str(row.get("severity") or "High").strip(),
        enabled=enabled,
    )


def load_rules(path: str | Path) -> list[Rule]:
    """Load enabled rules from an .xlsx (first sheet) or .csv workbook."""
    path = Path(path)
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as fh:
            rows = [{_header_key(k): v for k, v in r.items()} for r in csv.DictReader(fh)]
    else:
        sheet = load_workbook(path, read_only=True, data_only=True).worksheets[0]
        values = list(sheet.iter_rows(values_only=True))
        headers = [_header_key(h) for h in values[0]]
        rows = [dict(zip(headers, r, strict=False)) for r in values[1:] if any(r)]
    return [rule for rule in map(_to_rule, rows) if rule.enabled]


def evaluate(rule: Rule, actual) -> bool:
    expected = rule.expected
    try:
        return float(actual) == float(expected)
    except (TypeError, ValueError):
        return str(actual).strip() == expected
