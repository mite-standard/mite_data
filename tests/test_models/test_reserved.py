from pathlib import Path

import pytest

from mite_data_lib.models.reserved import ReserveService, ProteinService


def test_reserve_service_valid():
    m = ReserveService(path=Path("tests/dummy_data/reserved/valid.json"))
    assert m.reserved.get("MITE9999999") is not None


def test_reserve_service_invalid():
    m = ReserveService(path=Path("tests/dummy_data/reserved/invalid.json"))
    with pytest.raises(RuntimeError):
        assert m.reserved


def test_protein_service_valid():
    m = ProteinService(path=Path("tests/dummy_data/metadata/mite_prot_accessions.csv"))
    assert m.proteins is not None


def test_protein_service_invalid():
    m = ProteinService(path=Path("tests/dummy_data/metadata/asdfas.csv"))
    with pytest.raises(RuntimeError):
        assert m.proteins
