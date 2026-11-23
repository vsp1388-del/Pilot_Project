from decimal import Decimal

from pilot_framework.compare import reconcile
from pilot_framework.mappings import ColumnMapping, TableMapping

MAPPING = TableMapping(
    name="customers",
    source_table="cust_master",
    target_table="customer",
    source_key="cust_id",
    target_key="customer_id",
    columns=(
        ColumnMapping("first_nm", "first_name"),
        ColumnMapping("balance", "balance"),
        ColumnMapping("status_cd", "status", {"A": "ACTIVE", "I": "INACTIVE"}),
    ),
)


def src(key, name="Ann", balance=Decimal("10.50"), status="A"):
    return {"cust_id": key, "first_nm": name, "balance": balance, "status_cd": status}


def tgt(key, name="Ann", balance=Decimal("10.50"), status="ACTIVE"):
    return {"customer_id": key, "first_name": name, "balance": balance, "status": status}


def test_matching_rows_pass_with_transform():
    result = reconcile(MAPPING, [src(1), src(2, status="I")], [tgt(1), tgt(2, status="INACTIVE")])
    assert result.passed
    assert (result.source_rows, result.target_rows) == (2, 2)


def test_missing_and_extra_keys_are_reported():
    result = reconcile(MAPPING, [src(1), src(2)], [tgt(1), tgt(3)])
    assert not result.passed
    assert result.missing_in_target == [2]
    assert result.extra_in_target == [3]


def test_value_mismatch_is_reported_per_column():
    result = reconcile(MAPPING, [src(1)], [tgt(1, name="Bob", status="INACTIVE")])
    assert {m["column"] for m in result.mismatches} == {"first_name", "status"}
    assert "first_name" in result.summary()


def test_whitespace_and_float_are_normalised():
    result = reconcile(MAPPING, [src(1, name="Ann  ", balance=10.5)], [tgt(1)])
    assert result.passed
