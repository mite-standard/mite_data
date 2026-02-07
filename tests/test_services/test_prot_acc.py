from pathlib import Path

import pytest

from mite_data_lib.services.derive_prot_accessions import DeriveProtAccessions


@pytest.fixture
def prot_acc_model():
    return DeriveProtAccessions(
        data=Path("tests/dummy_data/data"),
        dump=Path("tests/dummy_data/metadata"),
    )


def test_update_prot_acc(prot_acc_model):
    assert (
        prot_acc_model.update_from_entry(Path("tests/dummy_data/data/MITE0000000.json"))
        is None
    )
