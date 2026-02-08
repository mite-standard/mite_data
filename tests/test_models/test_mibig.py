from pathlib import Path

import pytest

from mite_data_lib.models.mibig import MIBiGProtService


def test_mibig_prot_valid():
    m = MIBiGProtService(path=Path("tests/dummy_data/mibig/valid.json"))
    assert m.mibig_proteins.get("BGC0000001") is not None


def test_mibig_prot_invalid():
    m = MIBiGProtService(path=Path("tests/dummy_data/mibig/invalid.json"))
    with pytest.raises(RuntimeError):
        assert m.mibig_proteins
