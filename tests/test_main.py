import pytest

from mite_data.main import main


def test_no_attrs(monkeypatch):
    monkeypatch.setattr("sys.argv", ["mite_data"])
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 0


def test_verboseness_valid1(monkeypatch):
    monkeypatch.setattr("sys.argv", ["mite_data", "-v", "DEBUG"])
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 0


def test_verboseness_valid2(monkeypatch):
    monkeypatch.setattr("sys.argv", ["mite_data", "--verboseness", "DEBUG"])
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 0


def test_verboseness_invalid(monkeypatch):
    monkeypatch.setattr("sys.argv", ["mite_data", "--verboseness", "FALSE"])
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 2
