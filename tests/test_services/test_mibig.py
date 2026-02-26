from pathlib import Path

import pytest

from mite_data_lib.services.mibig import MIBiGDataService


def test_mibig_prot_valid():
    m = MIBiGDataService(
        path=Path("tests/dummy_data/mibig_valid/"), version="4.0.1", record="abc"
    )
    assert m.mibig_proteins.get("BGC0000001") is not None


def test_mibig_prot_invalid():
    m = MIBiGDataService(
        path=Path("tests/dummy_data/mibig_invalid"), version="4.0.1", record="abc"
    )
    with pytest.raises(RuntimeError):
        assert m.mibig_proteins
