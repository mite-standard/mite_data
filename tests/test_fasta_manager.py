import os
from pathlib import Path

import pytest

from mite_data.modules.fasta_manager import FastaManager


@pytest.fixture
def fasta_manager():
    return FastaManager(
        src=Path(__file__).parent.joinpath("mock_src"),
        fasta=Path(__file__).parent.joinpath("mock_fasta"),
    )


# Integration


def test_update_all(fasta_manager):
    assert fasta_manager.update_all() is None


def test_update_single(fasta_manager):
    assert (
        fasta_manager.update_single(
            Path(__file__).parent.joinpath("mock_src/MITE0000000.json")
        )
        is None
    )


# unit


def test_download_ncbi(fasta_manager):
    fasta_manager.download_ncbi(mite_acc="MITE9999999", genpept_acc="AAD28496.1")
    path = fasta_manager.fasta.joinpath("MITE9999999.fasta")
    assert path.exists()
    os.remove(path)


def test_download_uniprot(fasta_manager):
    fasta_manager.download_uniprot(mite_acc="MITE9999999", uniprot_acc="Q9X2V9")
    path = fasta_manager.fasta.joinpath("MITE9999999.fasta")
    assert path.exists()
    os.remove(path)


def test_download_uniparc(fasta_manager):
    fasta_manager.download_uniprot(mite_acc="MITE9999999", uniprot_acc="UPI000E33162C")
    path = fasta_manager.fasta.joinpath("MITE9999999.fasta")
    assert path.exists()
    os.remove(path)
