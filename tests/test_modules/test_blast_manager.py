import os
from pathlib import Path
from urllib.error import HTTPError

import pytest

from mite_data.modules.fasta_manager import FastaManager


@pytest.fixture
def blast_manager():
    return FastaManager(
        src=Path(__file__).parent.parent.joinpath(
            "example_files/example_metadata.json"
        ),
        target_download=Path(__file__).parent.parent.joinpath("example_files/"),
        target_blast=Path(__file__).parent.parent.joinpath("example_files/"),
    )


def test_extract_accessions_valid(blast_manager):
    blast_manager.extract_accessions()
    assert len(blast_manager.genpept_acc) == 1
    assert len(blast_manager.uniprot_acc) == 1


def test_extract_accessions_invalid(blast_manager):
    blast_manager.src = Path(__file__).parent.parent.joinpath(
        "example_files/example_invalid_metadata.json"
    )
    with pytest.raises(RuntimeError):
        blast_manager.extract_accessions()


@pytest.mark.slow
def test_download_ncbi(blast_manager):
    blast_manager.genpept_acc.append({"entry": "MITE00000", "acc": "CAK50792.1"})
    blast_manager.download_ncbi()
    assert Path("tests/example_files/MITE00000.fasta").exists()
    os.remove(Path("tests/example_files/MITE00000.fasta"))


@pytest.mark.slow
def test_download_uniprot(blast_manager):
    blast_manager.uniprot_acc.append({"entry": "MITE00000", "acc": "A0A346D7L2"})
    blast_manager.download_uniprot()
    assert Path("tests/example_files/MITE00000.fasta").exists()
    os.remove(Path("tests/example_files/MITE00000.fasta"))


@pytest.mark.slow
def test_download_uniparc(blast_manager):
    blast_manager.uniprot_acc.append({"entry": "MITE00000", "acc": "UPI000000000B"})
    blast_manager.download_uniprot()
    assert Path("tests/example_files/MITE00000.fasta").exists()
    os.remove(Path("tests/example_files/MITE00000.fasta"))


@pytest.mark.slow
def test_download_ncbi_fail(blast_manager):
    blast_manager.genpept_acc.append({"entry": "MITE00000", "acc": "AAAAAAAAAAAAA"})
    with pytest.raises(HTTPError):
        blast_manager.download_ncbi()


@pytest.mark.slow
def test_download_uniprot_fail(blast_manager):
    blast_manager.uniprot_acc.append({"entry": "MITE00000", "acc": "AAAAAAAAAAAAA"})
    with pytest.raises(RuntimeError):
        blast_manager.download_uniprot()


@pytest.mark.slow
def test_validate_nr_files(blast_manager):
    blast_manager.extract_accessions()
    blast_manager.download_ncbi()
    blast_manager.download_uniprot()
    assert blast_manager.validate_nr_files() is None
    os.remove(Path("tests/example_files/MITE0000020.fasta"))
    os.remove(Path("tests/example_files/MITE0000109.fasta"))
