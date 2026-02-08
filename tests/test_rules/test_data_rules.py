from mite_data_lib.rules import data_rules


def test_status_valid():
    e, w = data_rules.status({"status": "active"})
    assert not e


def test_status_invalid():
    e, w = data_rules.status({"status": "retired"})
    assert e


def test_accession_valid():
    e, w = data_rules.accession({"accession": "MITE1234567"})
    assert not e


def test_accession_invalid():
    e, w = data_rules.accession({"accession": "MITE9999999"})
    assert e
