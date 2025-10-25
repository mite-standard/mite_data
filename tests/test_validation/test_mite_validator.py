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
        reserved_path=Path(__file__).parent.joinpath("mock_reserved.json"),
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
    assert len(cicd_mngr.issues) == 0


def test_check_file_naming_invalid(cicd_mngr):
    cicd_mngr.check_file_naming(path=Path("asdfasd"))
    assert len(cicd_mngr.issues) == 1


def test_check_release_ready_valid(cicd_mngr, data):
    cicd_mngr.check_release_ready(data)
    assert len(cicd_mngr.issues) == 0


def test_check_release_ready_invalid(cicd_mngr, data):
    data_cp = copy.deepcopy(data)
    data_cp["status"] = "pending"
    data_cp["accession"] = "MITE9999999"
    cicd_mngr.check_release_ready(data_cp)
    assert len(cicd_mngr.issues) == 2


def test_check_duplicates_valid(cicd_mngr, data):
    cicd_mngr.check_duplicates(data)
    assert len(cicd_mngr.issues) == 0


def test_check_duplicates_invalid(cicd_mngr, data):
    cicd_mngr = copy.deepcopy(cicd_mngr)
    cicd_mngr.genpept["AAD28496.1"].append("MITE99999")
    cicd_mngr.uniprot["Q9X2V9"].append("MITE99999")
    cicd_mngr.check_duplicates(data)
    assert len(cicd_mngr.issues) == 2


def test_check_fasta_header_valid(cicd_mngr, data):
    cicd_mngr.check_fasta_header(data)
    assert len(cicd_mngr.issues) == 0


def test_check_fasta_header_genpept_invalid(cicd_mngr, data):
    data_cp = copy.deepcopy(data)
    data_cp["enzyme"]["databaseIds"]["genpept"] = "sdtzuio"
    cicd_mngr.check_fasta_header(data_cp)
    assert len(cicd_mngr.issues) == 1


def test_check_fasta_header_filepath_invalid(cicd_mngr, data):
    data_cp = copy.deepcopy(data)
    data_cp["accession"] = "qwertzuji"
    cicd_mngr.check_fasta_header(data_cp)
    assert len(cicd_mngr.issues) == 1


def test_validate_entries_passing_valid(cicd_mngr, data):
    cicd_mngr.validate_entries_passing(data)
    assert len(cicd_mngr.issues) == 0


def test_validate_entries_passing_invalid(cicd_mngr, data):
    data_cp = copy.deepcopy(data)
    data_cp["reactions"][0]["reactionSMARTS"] = r"[c]>>[c]"
    cicd_mngr.validate_entries_passing(data_cp)
    assert len(cicd_mngr.issues) == 1
