import pytest

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


def test_reserved_valid(ctx):
    e, w = data_rules.reserved({"accession": "MITE1234567"}, ctx=ctx)
    assert not e


def test_reserved_invalid(ctx):
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


@pytest.mark.download
def test_uniprot_exists_valid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"uniprot": "Q93KW1"}},
    }
    e, w = data_rules.uniprot_exists(data=d, ctx=ctx)
    assert not e


@pytest.mark.download
def test_uniprot_exists_invalid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"uniprot": "nonexisting"}},
    }
    e, w = data_rules.uniprot_exists(data=d, ctx=ctx)
    assert e


@pytest.mark.download
def test_genpept_exists_valid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"genpept": "AAK83184.1"}},
    }
    e, w = data_rules.genpept_exists(data=d, ctx=ctx)
    assert not e


@pytest.mark.download
def test_genpept_exists_invalid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"genpept": "nonexisting"}},
    }
    e, w = data_rules.genpept_exists(data=d, ctx=ctx)
    assert e


@pytest.mark.download
def test_wikidata_exists_valid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"wikidata": "Q12190"}},
    }
    e, w = data_rules.wikidata_exists(data=d, ctx=ctx)
    assert not e


@pytest.mark.download
def test_wikidata_exists_invalid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"wikidata": "nonexisting"}},
    }
    e, w = data_rules.wikidata_exists(data=d, ctx=ctx)
    assert e


@pytest.mark.download
def test_id_matching_valid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"genpept": "AAK83184.1", "uniprot": "Q93KW1"}},
    }
    e, w = data_rules.ids_matching(data=d, ctx=ctx)
    assert not e


@pytest.mark.download
def test_id_matching_invalid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"genpept": "AAK83184.1", "uniprot": "Q8KSX7"}},
    }
    e, w = data_rules.ids_matching(data=d, ctx=ctx)
    assert e


def test_mibig_exists_valid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"mibig": "BGC0000001"}},
    }
    e, w = data_rules.mibig_exists(data=d, ctx=ctx)
    assert not e


def test_mibig_exists_invalid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"mibig": "BGC0000000"}},
    }
    e, w = data_rules.mibig_exists(data=d, ctx=ctx)
    assert e


def test_check_mibig_protein_valid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"mibig": "BGC0000026", "genpept": "AAK83184.1"}},
    }
    e, w = data_rules.check_mibig_protein(data=d, ctx=ctx)
    assert not e


def test_check_mibig_protein_invalid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"mibig": "BGC0000026", "genpept": "nonexisting"}},
    }
    e, w = data_rules.check_mibig_protein(data=d, ctx=ctx)
    assert e


@pytest.mark.download
def test_check_rhea_valid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"uniprot": "Q8GED9"}},
        "reactions": [{"databaseIds": {"rhea": "35531"}}],
    }
    e, w = data_rules.check_rhea(data=d, ctx=ctx)
    assert not w


@pytest.mark.download
def test_check_rhea_invalid(ctx):
    d = {
        "accession": "MITE1234567",
        "enzyme": {"databaseIds": {"uniprot": "Q8GED9"}},
        "reactions": [{"databaseIds": {}}],
    }
    e, w = data_rules.check_rhea(data=d, ctx=ctx)
    assert w
