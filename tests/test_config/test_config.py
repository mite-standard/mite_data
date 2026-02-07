from pathlib import Path

import pytest

from mite_data_lib.config.config import Settings


@pytest.fixture
def settings():
    return Settings(data=Path("tests/dummy_data"))


def test_settings(settings):
    assert settings.mite_version is not None
