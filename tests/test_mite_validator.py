import copy
import json
from pathlib import Path

import pytest

from mite_data.validation.mite_validation import CicdManager


@pytest.fixture
def data():
    with open(Path(__file__).parent.joinpath("mock_src/MITE0000000.json")) as infile:
        return json.load(infile)


@pytest.fixture
def cicd_mngr():
    return CicdManager(
        src=Path(__file__).parent.joinpath("mock_src"),
        fasta=Path(__file__).parent.joinpath("mock_fasta"),
        reserved_path=Path(__file__).parent.joinpath(
            "mock_metadata/mock_reserved.json"
        ),
    )


# Integration


def test_instance(cicd_mngr):
    assert isinstance(cicd_mngr, CicdManager)
    assert len(cicd_mngr.genpept) == 1
    assert len(cicd_mngr.uniprot) == 1
    assert len(cicd_mngr.reserved) == 1


def test_run_file(cicd_mngr):
    assert (
        cicd_mngr.run_file(
            path=Path(__file__).parent.joinpath("mock_src/MITE0000000.json")
        )
        is None
    )


def test_run_dir(cicd_mngr):
    assert cicd_mngr.run_data_dir() is None


# Unit


def test_check_file_naming_valid(cicd_mngr):
    cicd_mngr.check_file_naming(path=Path("MITE0000001.json"))
    assert len(cicd_mngr.errors) == 0


def test_check_file_naming_invalid(cicd_mngr):
    cicd_mngr.check_file_naming(path=Path("asdfasd"))
    assert len(cicd_mngr.errors) == 1


def test_check_status_valid(cicd_mngr, data):
    cicd_mngr.check_status(data)
    assert len(cicd_mngr.errors) == 0


def test_check_status_invalid(cicd_mngr, data):
    data_cp = copy.deepcopy(data)
    data_cp["status"] = "pending"
    cicd_mngr.check_status(data_cp)
    assert len(cicd_mngr.errors) == 1


def test_check_accession_valid(cicd_mngr, data):
    cicd_mngr.check_accession(data)
    assert len(cicd_mngr.errors) == 0


def test_check_accession_invalid(cicd_mngr, data):
    data_cp = copy.deepcopy(data)
    data_cp["accession"] = "MITE9999999"
    cicd_mngr.check_accession(data_cp)
    assert len(cicd_mngr.errors) == 1


def test_check_duplicates_valid(cicd_mngr, data):
    cicd_mngr.check_duplicates(data)
    assert len(cicd_mngr.errors) == 0


def test_check_duplicates_invalid(cicd_mngr, data):
    cicd_mngr = copy.deepcopy(cicd_mngr)
    cicd_mngr.genpept["AAD28496.1"].append("MITE99999")
    cicd_mngr.uniprot["Q9X2V9"].append("MITE99999")
    cicd_mngr.check_duplicates(data)
    assert len(cicd_mngr.errors) == 2


def test_check_fasta_header_valid(cicd_mngr, data):
    cicd_mngr.check_fasta_header(data)
    assert len(cicd_mngr.errors) == 0


def test_check_fasta_header_genpept_invalid(cicd_mngr, data):
    data_cp = copy.deepcopy(data)
    data_cp["enzyme"]["databaseIds"]["genpept"] = "sdtzuio"
    cicd_mngr.check_fasta_header(data_cp)
    assert len(cicd_mngr.errors) == 1


def test_check_fasta_header_filepath_invalid(cicd_mngr, data):
    data_cp = copy.deepcopy(data)
    data_cp["accession"] = "qwertzuji"
    cicd_mngr.check_fasta_header(data_cp)
    assert len(cicd_mngr.errors) == 1


def test_validate_entries_passing_valid(cicd_mngr, data):
    cicd_mngr.validate_entries_passing(data)
    assert len(cicd_mngr.errors) == 0


def test_validate_entries_passing_invalid(cicd_mngr, data):
    data_cp = copy.deepcopy(data)
    data_cp["reactions"][0]["reactionSMARTS"] = r"[c]>>[c]"
    cicd_mngr.validate_entries_passing(data_cp)
    assert len(cicd_mngr.errors) == 1


def test_validate_db_ids_valid(cicd_mngr, data):
    cicd_mngr.validate_db_ids(data)
    assert len(cicd_mngr.errors) == 0


def test_validate_db_ids_invalid(cicd_mngr, data):
    data_cp = copy.deepcopy(data)
    data_cp["enzyme"]["databaseIds"]["genpept"] = "sdtzuio"
    cicd_mngr.validate_db_ids(data_cp)
    assert len(cicd_mngr.errors) == 1


def test_check_match_db_ids_valid(cicd_mngr, data):
    cicd_mngr.check_match_db_ids(data)
    assert len(cicd_mngr.warnings) == 0


def test_check_match_db_ids_uniparc_valid(cicd_mngr, data):
    data_cp = copy.deepcopy(data)
    data_cp["enzyme"]["databaseIds"]["uniprot"] = "UPI000006B1C3"
    cicd_mngr.check_match_db_ids(data_cp)
    assert len(cicd_mngr.warnings) == 0


def test_check_match_db_ids_uniprot_invalid(cicd_mngr, data):
    data_cp = copy.deepcopy(data)
    data_cp["enzyme"]["databaseIds"]["uniprot"] = "Q93KW5"
    cicd_mngr.check_match_db_ids(data_cp)
    assert len(cicd_mngr.warnings) == 1


def test_check_match_db_ids_uniprot_missing(cicd_mngr, data):
    data_cp = copy.deepcopy(data)
    data_cp["enzyme"]["databaseIds"].pop("uniprot")
    cicd_mngr.check_match_db_ids(data_cp)
    assert len(cicd_mngr.warnings) == 1


def test_check_match_db_ids_genpept_invalid(cicd_mngr, data):
    data_cp = copy.deepcopy(data)
    data_cp["enzyme"]["databaseIds"]["genpept"] = "AAK83180.1"
    cicd_mngr.check_match_db_ids(data_cp)
    assert len(cicd_mngr.warnings) == 1


def test_check_match_db_ids_genpept_missing(cicd_mngr, data):
    data_cp = copy.deepcopy(data)
    data_cp["enzyme"]["databaseIds"].pop("genpept")
    cicd_mngr.check_match_db_ids(data_cp)
    assert len(cicd_mngr.warnings) == 1
