from pathlib import Path

from mite_data_lib.rules import repo_rules

data_path = Path("tests/dummy_data/data/")


def test_naming_valid():
    e, w = repo_rules.naming(data_path / "MITE0000000.json")
    assert not e


def test_naming_invalid():
    e, w = repo_rules.naming(data_path / "invalid.json")
    assert e
