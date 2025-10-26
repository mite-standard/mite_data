import json
import shutil
from pathlib import Path

import pytest

from mite_data.main import MibigManager, RunManager


@pytest.fixture
def data():
    with open(Path(__file__).parent.joinpath("mock_src/MITE0000000.json")) as infile:
        return json.load(infile)


@pytest.fixture
def run_mngr():
    return RunManager(
        src=Path(__file__).parent.joinpath("mock_src"),
        fasta=Path(__file__).parent.joinpath("mock_fasta"),
        meta=Path(__file__).parent.joinpath("mock_metadata"),
    )


# Integration


def test_instance(run_mngr):
    assert isinstance(run_mngr, RunManager)


def test_instance_mibig_fail():
    with pytest.raises(RuntimeError):
        MibigManager(
            mibig_record="https://zenodo.org/api/records/anfaosdaosid",
            mibig=Path(__file__).parent.joinpath("mibig"),
        )
    shutil.rmtree(Path(__file__).parent.joinpath("mibig"))


def test_run_file(run_mngr):
    with pytest.raises(SystemExit) as e:
        run_mngr.run_file(
            path=Path(__file__).parent.joinpath("mock_src/MITE0000000.json")
        )
    assert e.type == SystemExit
    assert e.value.code == 0


def test_run_data_dir(run_mngr):
    with pytest.raises(SystemExit) as e:
        run_mngr.run_data_dir()
    assert e.type == SystemExit
    assert e.value.code == 0
