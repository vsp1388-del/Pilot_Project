# pilot_project

A data validation framework built on Robot Framework. It checks a legacy **source** Postgres
database against a migrated **target** database. Postgres runs in Docker, and the whole suite
runs with a single command.

## What it checks

| Suite | Tag | Checks |
|---|---|---|
| `01_schema_validation` | `schema` | Every mapped column exists in the source and target tables |
| `02_row_counts` | `counts` | Source and target row counts match for each table |
| `03_data_reconciliation` | `reconciliation` | Rows are compared column by column on the business key, after transforms |
| `04_aggregate_checks` | `aggregates` | Balance and principal totals match |
| `05_data_quality` | `quality` | Mandatory columns have no NULLs; business keys are unique |
| `06_business_rules` | `rules` | SQL rules from `data/rules/business_rules.xlsx` |

## Layout

```
pilot_framework/   Reusable Python: config, DB client, mappings, reconciliation, rules loader
libraries/         DataValidationLibrary.py - Robot keywords built on pilot_framework
resources/         common.resource - shared settings and keywords for suites
tests/             Robot suites (above)
config/            mappings.yaml - source -> target table/column mapping and value transforms
data/rules/        business_rules.xlsx - Excel rule workbook
docker/postgres/   init SQL: creates pilot_source and pilot_target with sample data
scripts/           run_tests.sh / run_tests.bat, wait_for_db.py, summarize_results.py,
                   build_rules_workbook.py
unittests/         pytest tests for pilot_framework
results/           run output (git-ignored)
```

## Run everything in Docker

```
docker compose up --build --abort-on-container-exit --exit-code-from app
docker compose down -v
```

Results land in `results/`: `report.html`, `log.html`, `output.xml`, `summary.md` and
`summary.json`.

Postgres is published on host port **5433** so it doesn't clash with a local Postgres on 5432.
Set `PILOT_DB_PORT` in `.env` to change it. If Docker Hub rate-limits you, point the images at a
mirror, e.g. `POSTGRES_IMAGE=mirror.gcr.io/library/postgres:16-alpine` and
`PYTHON_IMAGE=mirror.gcr.io/library/python:3.12-slim`.

## Run locally against the Docker database (Windows)

```
py -3.12 -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt
copy .env.example .env          & rem set PILOT_DB_PASSWORD to match docker compose
docker compose up -d --wait db
scripts\run_tests.bat
scripts\run_tests.bat --include counts     & rem any robot options
```

On Linux or macOS, use `scripts/run_tests.sh` the same way. Set `PYTHON=.venv/bin/python` if
`python` isn't the venv interpreter.

## Extending

- **New table:** add its DDL and data to `docker/postgres/init/` (or point the `PILOT_*` env vars
  at real databases). Add a mapping to `config/mappings.yaml`, then add a row to the templated
  suites.
- **New rule:** add a row to `data/rules/business_rules.xlsx` (Rule ID, Description, Database =
  source/target, SQL returning one value, Expected, Severity, Enabled Y/N). Use a different
  workbook with `-v RULES_WORKBOOK:path/to/rules.xlsx`.
- **New keyword:** add a method to `libraries/DataValidationLibrary.py` and keep the logic in
  `pilot_framework/` so it can be unit tested.

## Development

```
pip install -r requirements-dev.txt
pre-commit install
pytest
```

CI (`.github/workflows/ci.yml`) runs pre-commit, the unit tests, and the full Docker validation
run. It uploads `results/` as an artifact.
