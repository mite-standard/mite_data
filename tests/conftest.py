from pathlib import Path

import pytest

from mite_data_lib.models.validation import ValidationContext
from mite_data_lib.models.reserved import ReserveService
from mite_data_lib.services.prot_accessions import ProtAccessionService


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
    )
