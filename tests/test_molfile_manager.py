import copy
import json
import os
from pathlib import Path

import pytest

from mite_data.modules.molfile_manager import MolFileManager


@pytest.fixture
def mlfl_mngr():
    return MolFileManager(
        src=Path(__file__).parent.joinpath("mock_src"),
        trgt=Path(__file__).parent.joinpath("mock_metadata"),
    )


# Integration


def test_instance(mlfl_mngr):
    assert isinstance(mlfl_mngr, MolFileManager)


def test_prepare_files(mlfl_mngr):
    mlfl_mngr.prepare_files()
    assert len(mlfl_mngr.smiles["mite_id"])


def test_dump_files(mlfl_mngr):
    mlfl_mngr.prepare_files()
    mlfl_mngr.dump_files()
    os.remove(mlfl_mngr.trgt.joinpath("dump_smiles.csv"))
    os.remove(mlfl_mngr.trgt.joinpath("dump_smarts.csv"))
    os.remove(mlfl_mngr.trgt.joinpath("substrate_list.pickle"))
    os.remove(mlfl_mngr.trgt.joinpath("product_list.pickle"))
    os.remove(mlfl_mngr.trgt.joinpath("reaction_fps.pickle"))
