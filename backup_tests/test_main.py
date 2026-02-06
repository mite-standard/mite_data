import shutil
from pathlib import Path

import pytest

from mite_data.main import MibigManager, RunManager


@pytest.fixture
def run_mngr():
    return RunManager()


# Integration


def test_instance(run_mngr):
    assert isinstance(run_mngr, RunManager)
