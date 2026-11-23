"""Regenerate data/rules/business_rules.xlsx from the starter rule set below.

Edit the workbook directly in Excel for day-to-day changes; this script only recreates the
starter version.
"""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

OUT = Path(__file__).resolve().parent.parent / "data" / "rules" / "business_rules.xlsx"

HEADERS = ["Rule ID", "Description", "Database", "SQL", "Expected", "Severity", "Enabled"]
RULES = [
    (
        "BR001",
        "No negative deposit balances",
        "target",
        "SELECT count(*) FROM deposit_account WHERE balance < 0",
        0,
        "High",
        "Y",
    ),
    (
        "BR002",
        "Every deposit account belongs to a customer",
        "target",
        "SELECT count(*) FROM deposit_account d LEFT JOIN customer c USING (customer_id) "
        "WHERE c.customer_id IS NULL",
        0,
        "High",
        "Y",
    ),
    (
        "BR003",
        "Every loan belongs to a customer",
        "target",
        "SELECT count(*) FROM loan l LEFT JOIN customer c USING (customer_id) "
        "WHERE c.customer_id IS NULL",
        0,
        "High",
        "Y",
    ),
    (
        "BR004",
        "Loan maturity date is after start date",
        "target",
        "SELECT count(*) FROM loan WHERE maturity_date <= start_date",
        0,
        "High",
        "Y",
    ),
    (
        "BR005",
        "Interest rate between 0 and 25 percent",
        "target",
        "SELECT count(*) FROM loan WHERE interest_rate NOT BETWEEN 0 AND 25",
        0,
        "Medium",
        "Y",
    ),
    (
        "BR006",
        "Deposit currency is USD",
        "target",
        "SELECT count(*) FROM deposit_account WHERE currency <> 'USD'",
        0,
        "Medium",
        "Y",
    ),
    (
        "BR007",
        "Customer status is ACTIVE or INACTIVE",
        "target",
        "SELECT count(*) FROM customer WHERE status NOT IN ('ACTIVE', 'INACTIVE')",
        0,
        "High",
        "Y",
    ),
    (
        "BR008",
        "Customer email has a valid format",
        "target",
        "SELECT count(*) FROM customer WHERE email !~ '^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$'",
        0,
        "Low",
        "Y",
    ),
    (
        "BR009",
        "Source loan status codes are O or C",
        "source",
        "SELECT count(*) FROM loan_acct WHERE status_cd NOT IN ('O', 'C')",
        0,
        "Medium",
        "Y",
    ),
]


def main():
    wb = Workbook()
    ws = wb.active
    ws.title = "Rules"
    ws.append(HEADERS)
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for rule in RULES:
        ws.append(list(rule))
    for col, width in zip("ABCDEFG", (10, 45, 10, 90, 10, 10, 9), strict=True):
        ws.column_dimensions[col].width = width
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
