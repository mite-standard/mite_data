import copy
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
            Path(__file__).parent.joinpath("mock_src/MITE0000000.json"),
        )
        is None
    )


# unit


def test_download_ncbi(fasta_manager):
    path, content = fasta_manager.download_ncbi(
        mite_acc="MITE9999999",
        genpept_acc="AAD28496.1",
    )
    assert isinstance(path, Path)
    assert content


def test_download_uniprot(fasta_manager):
    path, content = fasta_manager.download_uniprot(
        mite_acc="MITE9999999",
        uniprot_acc="Q9X2V9",
    )
    assert isinstance(path, Path)
    assert content


def test_download_ncbi_timeout(fasta_manager):
    mngr = copy.deepcopy(fasta_manager)
    mngr.timeout = 0.000001
    with pytest.raises(RuntimeError):
        mngr.download_ncbi(mite_acc="MITE9999999", genpept_acc="AAD28496.1")


def test_download_uniprot_timeout(fasta_manager):
    mngr = copy.deepcopy(fasta_manager)
    mngr.timeout = 0.000001
    with pytest.raises(RuntimeError):
        mngr.download_uniprot(mite_acc="MITE9999999", uniprot_acc="Q9X2V9")


def test_download_uniparc(fasta_manager):
    path, content = fasta_manager.download_uniprot(
        mite_acc="MITE9999999",
        uniprot_acc="UPI000E33162C",
    )
    assert isinstance(path, Path)
    assert content
