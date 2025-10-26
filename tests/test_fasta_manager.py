import os
from pathlib import Path

import pytest

from mite_data.modules.fasta_manager import FastaManager


@pytest.fixture
def example_files():
    return Path(__file__).parent.parent.joinpath("example_files/")


@pytest.fixture
def fasta_manager(example_files):
    return FastaManager(
        src=example_files.joinpath("example_metadata.json"),
        target_download=example_files,
        target_blast=example_files,
    )


def test_extract_accessions_valid(fasta_manager):
    fasta_manager.extract_accessions()
    assert len(fasta_manager.genpept_acc) == 1
    assert len(fasta_manager.uniprot_acc) == 1


def test_extract_accessions_invalid(fasta_manager, example_files):
    fasta_manager.src = example_files.joinpath("example_invalid_metadata.json")
    with pytest.raises(RuntimeError):
        fasta_manager.extract_accessions()


def test_download_ncbi(fasta_manager, example_files):
    fasta_manager.genpept_acc.append({"entry": "MITE00000", "acc": "CAK50792.1"})
    fasta_manager.download_ncbi()
    download = example_files.joinpath("MITE00000.fasta")
    assert download.exists()
    os.remove(download)


def test_download_uniprot(fasta_manager, example_files):
    fasta_manager.uniprot_acc.append({"entry": "MITE00000", "acc": "UPI000E33162C"})
    fasta_manager.download_uniprot()
    download = example_files.joinpath("MITE00000.fasta")
    assert download.exists()
    os.remove(download)


def test_download_uniparc(fasta_manager, example_files):
    fasta_manager.uniprot_acc.append({"entry": "MITE00000", "acc": "UPI000000000B"})
    fasta_manager.download_uniprot()
    download = example_files.joinpath("MITE00000.fasta")
    assert download.exists()
    os.remove(download)


def test_download_ncbi_fail(fasta_manager):
    fasta_manager.genpept_acc.append({"entry": "MITE00000", "acc": "AAAAAAAAAAAAA"})
    with pytest.raises(ValueError):
        fasta_manager.download_ncbi()


def test_download_uniprot_fail(fasta_manager):
    fasta_manager.uniprot_acc.append({"entry": "MITE00000", "acc": "AAAAAAAAAAAAA"})
    with pytest.raises(RuntimeError):
        fasta_manager.download_uniprot()
