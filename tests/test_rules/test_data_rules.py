from mite_data_lib.rules import data_rules


def test_status_valid(ctx):
    e, w = data_rules.status(
        data={"accession": "MITE1234567", "status": "active"}, ctx=ctx
    )
    assert not e


def test_status_invalid(ctx):
    e, w = data_rules.status(
        data={"accession": "MITE1234567", "status": "retired"}, ctx=ctx
    )
    assert e


def test_accession_valid(ctx):
    e, w = data_rules.reserved({"accession": "MITE1234567"}, ctx=ctx)
    assert not e


def test_accession_invalid(ctx):
    e, w = data_rules.reserved({"accession": "MITE9999999"}, ctx=ctx)
    assert e


def test_duplicate_genpept_valid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"genpept": "AAK83184.1"}},
    }
    e, w = data_rules.duplicate_genpept(data=d, ctx=ctx)
    assert e


def test_duplicate_genpept_invalid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"genpept": "nonexisting"}},
    }
    e, w = data_rules.duplicate_genpept(data=d, ctx=ctx)
    assert not e


def test_duplicate_uniprot_valid(ctx):
    d = {"accession": "MITE1234567", "enzyme": {"databaseIds": {"uniprot": "Q93KW1"}}}
    e, w = data_rules.duplicate_uniprot(data=d, ctx=ctx)
    assert e


def test_duplicate_uniprot_invalid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"uniprot": "nonexisting"}},
    }
    e, w = data_rules.duplicate_uniprot(data=d, ctx=ctx)
    assert not e


def test_uniprot_exists_valid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"uniprot": "Q93KW1"}},
    }
    e, w = data_rules.uniprot_exists(data=d, ctx=ctx)
    assert not e


def test_uniprot_exists_invalid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"uniprot": "nonexisting"}},
    }
    e, w = data_rules.uniprot_exists(data=d, ctx=ctx)
    assert e
