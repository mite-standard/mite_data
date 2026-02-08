from mite_data_lib.rules import data_rules


def test_status_valid():
    e, w = data_rules.status({"status": "active"})
    assert not any([e, w])


def test_status_invalid():
    e, w = data_rules.status({"status": "retired"})
    assert e
