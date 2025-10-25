import pytest

from mite_data.validation.mite_validation import CicdManager


def test_instance():
    assert isinstance(CicdManager(), CicdManager)
