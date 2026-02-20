from pathlib import Path

import pytest

from mite_data_lib.models.validation import ValidationContext
from mite_data_lib.services.reserved import ReserveService
from mite_data_lib.services.prot_accessions import ProtAccessionService
from mite_data_lib.services.sequence import SequenceService
from mite_data_lib.services.mibig import MIBiGDataService


def pytest_addoption(parser):
    parser.addoption(
        "--download",
        action="store_true",
        default=False,
        help="run tests fetching sources",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "download: mark test as fetching from external sources"
    )


def pytest_runtest_setup(item):
    if "download" in item.keywords and not item.config.getoption("--download"):
        pytest.skip("test requires '--download' option to run")


@pytest.fixture
def ctx():
    return ValidationContext(
        reserved=ReserveService(
            path=Path("tests/dummy_data/reserved/valid.json")
        ).reserved,
        proteins=ProtAccessionService(
            data=Path("tests/dummy_data/data"),
            dump=Path("tests/dummy_data/metadata"),
            prot_acc=Path("tests/dummy_data/metadata/mite_prot_accessions.csv"),
            metadata=Path("tests/dummy_data/metadata/artifact_metadata.json"),
        ).proteins,
        seq_service=SequenceService(fasta=Path("tests/dummy_data/fasta")),
        mibig_proteins=MIBiGDataService(
            version="4.0.1",
            path=Path("tests/dummy_data/mibig_valid"),
        ).mibig_proteins,
    )
