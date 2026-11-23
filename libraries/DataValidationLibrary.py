from robot.api import logger
from robot.api.deco import keyword, library

from pilot_framework.compare import reconcile
from pilot_framework.config import db_settings
from pilot_framework.db import Database
from pilot_framework.mappings import load_mappings
from pilot_framework.rules import evaluate, load_rules


@library(scope="GLOBAL")
class DataValidationLibrary:
    """Robot keywords for source-vs-target data validation on Postgres."""

    def __init__(self, mappings_file: str | None = None):
        self._mappings = load_mappings(mappings_file) if mappings_file else load_mappings()
        self._dbs: dict[str, Database] = {}

    def _db(self, role: str) -> Database:
        role = role.lower()
        if role not in self._dbs:
            self._dbs[role] = Database(db_settings(role)).connect()
        return self._dbs[role]

    def _mapping(self, name: str):
        try:
            return self._mappings[name]
        except KeyError:
            raise AssertionError(f"No mapping '{name}'. Known: {sorted(self._mappings)}") from None

    @keyword
    def connect_to_databases(self):
        for role in ("source", "target"):
            db = self._db(role)
            logger.info(f"Connected to {role} database '{db.settings.dbname}'")

    @keyword
    def disconnect_from_databases(self):
        for db in self._dbs.values():
            db.close()
        self._dbs.clear()

    @keyword
    def query_scalar(self, database: str, sql: str):
        return self._db(database).scalar(sql)

    @keyword
    def target_schema_should_match_mapping(self, mapping_name: str):
        mapping = self._mapping(mapping_name)
        source_cols = [mapping.source_key] + [c.source for c in mapping.columns]
        target_cols = [mapping.target_key] + [c.target for c in mapping.columns]
        for role, table, expected in (
            ("source", mapping.source_table, source_cols),
            ("target", mapping.target_table, target_cols),
        ):
            actual = self._db(role).columns(table)
            if not actual:
                raise AssertionError(f"{role} table '{table}' does not exist")
            missing = [c for c in expected if c not in actual]
            if missing:
                raise AssertionError(f"{role} table '{table}' is missing columns {missing}")
            logger.info(f"{role}.{table} columns: {actual}")

    @keyword
    def row_counts_should_match(self, mapping_name: str):
        mapping = self._mapping(mapping_name)
        src = self._db("source").scalar(f'SELECT count(*) FROM "{mapping.source_table}"')
        tgt = self._db("target").scalar(f'SELECT count(*) FROM "{mapping.target_table}"')
        logger.info(f"{mapping_name}: source={src} target={tgt}")
        if src == 0:
            raise AssertionError(f"Source table '{mapping.source_table}' is empty")
        if src != tgt:
            raise AssertionError(f"{mapping_name}: source has {src} rows, target has {tgt}")

    @keyword
    def table_data_should_reconcile(self, mapping_name: str):
        mapping = self._mapping(mapping_name)
        src_rows = self._db("source").query(f'SELECT * FROM "{mapping.source_table}"')
        tgt_rows = self._db("target").query(f'SELECT * FROM "{mapping.target_table}"')
        result = reconcile(mapping, src_rows, tgt_rows)
        logger.info(result.summary())
        if not result.passed:
            raise AssertionError(result.summary())

    @keyword
    def column_totals_should_match(self, mapping_name: str, source_column: str, target_column: str):
        mapping = self._mapping(mapping_name)
        src = self._db("source").scalar(
            f'SELECT coalesce(sum("{source_column}"), 0) FROM "{mapping.source_table}"'
        )
        tgt = self._db("target").scalar(
            f'SELECT coalesce(sum("{target_column}"), 0) FROM "{mapping.target_table}"'
        )
        logger.info(f"sum {source_column}={src} sum {target_column}={tgt}")
        if src != tgt:
            raise AssertionError(
                f"{mapping_name}: total {source_column}={src} vs {target_column}={tgt}"
            )

    @keyword
    def column_should_not_contain_nulls(self, database: str, table: str, column: str):
        nulls = self._db(database).scalar(
            f'SELECT count(*) FROM "{table}" WHERE "{column}" IS NULL'
        )
        if nulls:
            raise AssertionError(f"{database}.{table}.{column} has {nulls} NULL value(s)")

    @keyword
    def column_values_should_be_unique(self, database: str, table: str, column: str):
        dupes = self._db(database).scalar(
            f'SELECT count(*) FROM (SELECT "{column}" FROM "{table}" '
            f'GROUP BY "{column}" HAVING count(*) > 1) d'
        )
        if dupes:
            raise AssertionError(f"{database}.{table}.{column} has {dupes} duplicated value(s)")

    @keyword
    def load_business_rules(self, workbook: str):
        rules = load_rules(workbook)
        if not rules:
            raise AssertionError(f"No enabled rules found in {workbook}")
        logger.info(f"Loaded {len(rules)} rule(s) from {workbook}")
        return rules

    @keyword
    def business_rule_should_pass(self, rule):
        actual = self._db(rule.database).scalar(rule.sql)
        logger.info(f"{rule.rule_id} [{rule.severity}] {rule.description}: actual={actual}")
        if not evaluate(rule, actual):
            raise AssertionError(
                f"{rule.rule_id} {rule.description}: expected {rule.expected}, got {actual}"
            )
