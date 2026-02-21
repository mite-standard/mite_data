from pathlib import Path

import pytest

from mite_data_lib.models.validation import ArtifactContext
from mite_data_lib.rules import fasta_rules


@pytest.fixture
def art_ctx() -> ArtifactContext:
    return ArtifactContext(
        data=Path("tests/dummy_data/data"),
        fasta=Path("tests/dummy_data/fasta"),
        metadata=Path("tests/dummy_data/metadata"),
    )


def test_fasta_check_valid(art_ctx):
    d = {
        "status": "active",
        "accession": "MITE0000000",
        "enzyme": {"databaseIds": {"uniprot": "Q93KW1"}},
    }
    e, w = fasta_rules.fasta_check(data=d, ctx=art_ctx)
    assert not e


def test_fasta_check_no_fasta():
    ctx = ArtifactContext(
        data=Path("tests/dummy_data/data"),
        fasta=Path("tests/dummy_data/reserved"),
        metadata=Path("tests/dummy_data/metadata"),
    )
    d = {
        "status": "active",
        "accession": "MITE0000000",
        "enzyme": {"databaseIds": {"uniprot": "Q93KW1"}},
    }
    e, w = fasta_rules.fasta_check(data=d, ctx=ctx)
    assert e


def test_fasta_check_not_active(art_ctx):
    d = {
        "status": "retired",
        "accession": "MITE0000000",
        "enzyme": {"databaseIds": {"uniprot": "Q93KW1"}},
    }
    e, w = fasta_rules.fasta_check(data=d, ctx=art_ctx)
    assert e


def test_fasta_check_header_mismatch(art_ctx):
    d = {
        "status": "active",
        "accession": "MITE0000000",
        "enzyme": {"databaseIds": {"uniprot": "asdfasd"}},
    }
    e, w = fasta_rules.fasta_check(data=d, ctx=art_ctx)
    assert e
