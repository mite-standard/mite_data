from pathlib import Path

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


def test_extract_accessions(blast_manager):
    blast_manager.extract_accessions()
    assert len(blast_manager.genpept_acc) == 1
    assert len(blast_manager.uniprot_acc) == 1


def test_download_ncbi(blast_manager):
    blast_manager.uniprot_acc.append(("CAK50792.1", "A0A346D7L2"))
    assert blast_manager.download_ncbi() is None


def test_download_uniprot(blast_manager):
    blast_manager.uniprot_acc.append(("MITE00000", "A0A346D7L2"))
    assert blast_manager.download_uniprot() is None


def test_download_uniparc(blast_manager):
    blast_manager.uniprot_acc.append(("MITE00000", "UPI000000000B"))
    assert blast_manager.download_uniprot() is None


def test_download_ncbi_fail(blast_manager):
    pass


def test_download_uniprot_fail(blast_manager):
    pass
