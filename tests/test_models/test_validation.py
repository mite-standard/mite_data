from pathlib import Path

import pytest

from mite_data_lib.models.validation import ReserveService


def test_reserve_service_valid():
    m = ReserveService(path=Path("tests/dummy_data/reserved/valid.json"))
    assert m.reserved.get("MITE9999999") is not None


def test_reserve_service_invalid():
    m = ReserveService(path=Path("tests/dummy_data/reserved/invalid.json"))
    with pytest.raises(RuntimeError):
        assert m.reserved
