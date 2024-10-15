import os
from pathlib import Path
from urllib.error import HTTPError

import pytest

from mite_data.modules.blast_manager import BlastManager


@pytest.fixture
def blast_manager():
    return BlastManager(
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
    blast_manager.genpept_acc.append(("MITE00000", "CAK50792.1"))
    blast_manager.download_ncbi()
    assert Path("tests/example_files/CAK50792.1.fasta").exists()
    os.remove(Path("tests/example_files/CAK50792.1.fasta"))


@pytest.mark.slow
def test_download_uniprot(blast_manager):
    blast_manager.uniprot_acc.append(("MITE00000", "A0A346D7L2"))
    blast_manager.download_uniprot()
    assert Path("tests/example_files/A0A346D7L2.fasta").exists()
    os.remove(Path("tests/example_files/A0A346D7L2.fasta"))


@pytest.mark.slow
def test_download_uniparc(blast_manager):
    blast_manager.uniprot_acc.append(("MITE00000", "UPI000000000B"))
    blast_manager.download_uniprot()
    assert Path("tests/example_files/UPI000000000B.fasta").exists()
    os.remove(Path("tests/example_files/UPI000000000B.fasta"))


@pytest.mark.slow
def test_download_ncbi_fail(blast_manager):
    blast_manager.genpept_acc.append(("MITE00000", "AAAAAAAAAAAAA"))
    with pytest.raises(HTTPError):
        blast_manager.download_ncbi()


@pytest.mark.slow
def test_download_uniprot_fail(blast_manager):
    blast_manager.uniprot_acc.append(("MITE00000", "AAAAAAAAAAAAA"))
    with pytest.raises(RuntimeError):
        blast_manager.download_uniprot()


@pytest.mark.slow
def test_validate_nr_files(blast_manager):
    blast_manager.extract_accessions()
    blast_manager.download_ncbi()
    blast_manager.download_uniprot()
    assert blast_manager.validate_nr_files() is None
    os.remove(Path("tests/example_files/CAK50792.1.fasta"))
    os.remove(Path("tests/example_files/A0A346D7L2.fasta"))


@pytest.mark.slow
def test_concat_fasta_files_valid(blast_manager):
    blast_manager.extract_accessions()
    blast_manager.download_ncbi()
    blast_manager.download_uniprot()
    blast_manager.concat_fasta_files()
    assert Path("tests/example_files/mite_enzymes_concat.fasta").stat().st_size != 0
    os.remove(Path("tests/example_files/mite_enzymes_concat.fasta"))
    os.remove(Path("tests/example_files/CAK50792.1.fasta"))
    os.remove(Path("tests/example_files/A0A346D7L2.fasta"))


@pytest.mark.slow
def test_generate_blast_db(blast_manager):
    blast_manager.extract_accessions()
    blast_manager.download_ncbi()
    blast_manager.download_uniprot()
    blast_manager.concat_fasta_files()
    assert blast_manager.generate_blast_db() is None
    os.remove(Path("tests/example_files/mite_enzymes_concat.fasta"))
    os.remove(Path("tests/example_files/CAK50792.1.fasta"))
    os.remove(Path("tests/example_files/A0A346D7L2.fasta"))
