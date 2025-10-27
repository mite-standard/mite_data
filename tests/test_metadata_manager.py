import copy
import json
import shutil
from pathlib import Path

import pytest

from mite_data.modules.metadata_manager import MetadataManager


@pytest.fixture
def data():
    with open(Path(__file__).parent.joinpath("mock_src/MITE0000000.json")) as infile:
        return json.load(infile)


@pytest.fixture
def meta_mngr():
    return MetadataManager(
        src=Path(__file__).parent.joinpath("mock_src"),
        meta=Path(__file__).parent.joinpath("mock_metadata"),
        mibig=Path(__file__).parent.joinpath("mock_metadata"),
    )


# Integration


def test_instance(meta_mngr):
    assert isinstance(meta_mngr, MetadataManager)
    assert meta_mngr.mibig_data
    assert meta_mngr.meta_gen
    assert meta_mngr.meta_mibig


# Unit


def test_extr_meta_gen(meta_mngr, data):
    cp_data = copy.deepcopy(data)
    cp_data["accession"] = "MITE9999999"
    meta_mngr.extr_meta_gen(cp_data)
    assert meta_mngr.meta_gen["entries"]["MITE9999999"]


def test_extr_meta_mibig(meta_mngr, data):
    cp_data = copy.deepcopy(data)
    cp_data["accession"] = "MITE9999999"
    meta_mngr.extr_meta_mibig(cp_data)
    meta_mngr.extr_meta_mibig(cp_data)
    assert len(meta_mngr.meta_mibig["entries"]["BGC0000581"]) == 3


def test_get_taxonomy(meta_mngr, data):
    origin = meta_mngr.get_taxonomy(data)
    assert origin["family"] == "Enterobacteriaceae"
