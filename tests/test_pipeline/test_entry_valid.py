from pathlib import Path

import pytest

from pipeline.entry_valid import EntryValidRunner

data_path = Path("tests/dummy_data/data/")


@pytest.fixture
def entry_valid_runner():
    return EntryValidRunner()


def test_load_validate_valid(entry_valid_runner):
    assert (
        entry_valid_runner._load_and_validate_schema(data_path / "MITE0000000.json")
        is not None
    )


def test_load_validate_invalid_file(entry_valid_runner):
    with pytest.raises(FileNotFoundError):
        entry_valid_runner._load_and_validate_schema(data_path / "aasfasd")


def test_load_validate_invalid_json(entry_valid_runner):
    with pytest.raises(RuntimeError):
        entry_valid_runner._load_and_validate_schema(data_path / "invalid.json")
