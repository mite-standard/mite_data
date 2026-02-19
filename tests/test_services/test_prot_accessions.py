from pathlib import Path

import pytest

from mite_data_lib.services.prot_accessions import ProtAccessionService


@pytest.fixture
def prot_acc_model():
    return ProtAccessionService(
        data=Path("tests/dummy_data/data"),
        dump=Path("tests/dummy_data/metadata"),
        metadata=Path("tests/dummy_data/metadata/artifact_metadata.json"),
        prot_acc=Path("tests/dummy_data/metadata/mite_prot_accessions.csv"),
    )


def test_update_prot_acc(prot_acc_model):
    assert (
        prot_acc_model.update_from_entry(Path("tests/dummy_data/data/MITE0000000.json"))
        is None
    )


def test_proteins_valid(prot_acc_model):
    assert prot_acc_model.proteins is not None


def test_proteins_invalid():
    m = ProtAccessionService(
        prot_acc=Path("tests/dummy_data/metadata/mite_prot_accessions.csv"),
        metadata=Path("tests/dummy_data/metadata/invalid.json"),
    )
    with pytest.raises(RuntimeError):
        assert m.proteins
