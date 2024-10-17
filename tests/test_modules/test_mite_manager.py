from pathlib import Path

import pytest

from mite_data.modules.mite_manager import MiteManager


@pytest.fixture
def mite_manager():
    return MiteManager(src=Path(__file__).parent.parent.joinpath("example_files/"))


def test_run(mite_manager):
    assert mite_manager.run() is None
