import pytest

from pilot_framework.config import db_settings
from pilot_framework.mappings import load_mappings


def test_db_settings_from_env(monkeypatch):
    monkeypatch.setenv("PILOT_DB_PORT", "6000")
    monkeypatch.setenv("PILOT_TARGET_DB", "tgt")
    settings = db_settings("target")
    assert settings.port == 6000
    assert settings.dbname == "tgt"


def test_unknown_role_rejected():
    with pytest.raises(ValueError):
        db_settings("prod")


def test_project_mappings_load():
    mappings = load_mappings()
    assert set(mappings) == {"customers", "deposit_accounts", "loans"}
    status = next(c for c in mappings["customers"].columns if c.target == "status")
    assert status.transform == {"A": "ACTIVE", "I": "INACTIVE"}
