import pytest
from openpyxl import Workbook

from pilot_framework.rules import Rule, evaluate, load_rules

HEADERS = ["Rule ID", "Description", "Database", "SQL", "Expected", "Severity", "Enabled"]


def test_load_xlsx_skips_disabled_rules(tmp_path):
    path = tmp_path / "rules.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.append(HEADERS)
    ws.append(["R1", "first", "target", "SELECT 0", 0, "High", "Y"])
    ws.append(["R2", "off", "source", "SELECT 1", 1, "Low", "N"])
    wb.save(path)
    rules = load_rules(path)
    assert [r.rule_id for r in rules] == ["R1"]
    assert rules[0].expected == "0"


def test_load_csv(tmp_path):
    path = tmp_path / "rules.csv"
    path.write_text(",".join(HEADERS) + "\nR1,desc,Source,SELECT 1,1,Medium,\n", encoding="utf-8")
    (rule,) = load_rules(path)
    assert rule.database == "source"
    assert rule.enabled


def test_invalid_database_is_rejected(tmp_path):
    path = tmp_path / "rules.csv"
    path.write_text(",".join(HEADERS) + "\nR1,desc,prod,SELECT 1,1,High,Y\n", encoding="utf-8")
    with pytest.raises(ValueError, match="source or target"):
        load_rules(path)


@pytest.mark.parametrize(
    ("expected", "actual", "ok"),
    [
        ("0", 0, True),
        ("0", 3, False),
        ("1.5", "1.50", True),
        ("OK", "OK", True),
        ("OK", "NO", False),
    ],
)
def test_evaluate(expected, actual, ok):
    rule = Rule("R", "d", "target", "SELECT 1", expected)
    assert evaluate(rule, actual) is ok
