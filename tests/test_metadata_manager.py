import json
import shutil
from pathlib import Path

import pytest

from mite_data.modules.metadata_manager import MetadataManager


@pytest.fixture
def meta_mngr():
    return MetadataManager(
        src=Path(__file__).parent.joinpath("mock_src"),
        metadata=Path(__file__).parent.joinpath("mock_metadata"),
        mibig=Path(__file__).parent.joinpath("mock_metadata"),
    )


# Integration


def test_instance(meta_mngr):
    assert isinstance(meta_mngr, MetadataManager)
    assert meta_mngr.mibig_data
    assert meta_mngr.meta_gen
    assert meta_mngr.meta_mibig
