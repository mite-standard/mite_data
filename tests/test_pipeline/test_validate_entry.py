from pathlib import Path

import pytest

from pipeline.validate_entry import ValidateEntryRunner, main

data_path = Path("tests/dummy_data/data/")


@pytest.fixture
def entry_valid_runner():
    return ValidateEntryRunner()


@pytest.mark.download
def test_entry_valid(entry_valid_runner, ctx):
    e, w = entry_valid_runner.run(path=data_path / "MITE0000000.json", ctx=ctx)
    assert not all([e, w])


def test_load_validate_invalid_file(entry_valid_runner):
    with pytest.raises(FileNotFoundError):
        entry_valid_runner._load_and_validate_schema(data_path / "aasfasd")


def test_load_validate_invalid_json(entry_valid_runner):
    with pytest.raises(RuntimeError):
        entry_valid_runner._load_and_validate_schema(data_path / "invalid.json")


@pytest.mark.download
def test_main_valid(ctx):
    assert main(entries=[str(data_path / "MITE0000000.json")], ctx=ctx) is None
