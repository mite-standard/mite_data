from pathlib import Path

import pytest

from mite_data_lib.services.derive_prot_accessions import DeriveProtAccessions


@pytest.fixture
def prot_acc_model():
    return DeriveProtAccessions()


def test_update_prot_acc(prot_acc_model):
    assert (
        prot_acc_model.update_prot_acc(Path("tests/dummy_data/data/MITE0000000.json"))
        is None
    )
