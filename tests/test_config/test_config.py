from pathlib import Path

import pytest

from src.config.config import Settings


@pytest.fixture
def settings():
    return Settings(data=Path("tests/dummy_data"))


def test_settings(settings):
    assert settings.timeout is not None
