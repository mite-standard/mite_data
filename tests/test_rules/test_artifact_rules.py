from pathlib import Path

import pytest

from mite_data_lib.models.validation import ArtifactContext
from mite_data_lib.rules import artifact_rules


@pytest.fixture
def art_ctx() -> ArtifactContext:
    return ArtifactContext(
        data=Path("tests/dummy_data/data"), fasta=Path("tests/dummy_data/fasta")
    )


def test_fasta_check_valid(art_ctx):
    path = Path("tests/dummy_data/data/MITE0000000.json")
    e, w = artifact_rules.fasta_check(path=path, ctx=art_ctx)
    assert not e


def test_fasta_check_invalid():
    ctx = ArtifactContext(
        data=Path("tests/dummy_data/data"), fasta=Path("tests/dummy_data/reserved")
    )
    path = Path("tests/dummy_data/data/MITE0000000.json")
    e, w = artifact_rules.fasta_check(path=path, ctx=ctx)
    assert e


def test_fasta_affiliation_valid(art_ctx):
    path = Path("tests/dummy_data/data/MITE0000000.json")
    e, w = artifact_rules.fasta_affiliation(path=path, ctx=art_ctx)
    assert not w


def test_fasta_affiliation_invalid():
    ctx = ArtifactContext(
        data=Path("tests/dummy_data/reserved"), fasta=Path("tests/dummy_data/fasta")
    )
    path = Path("tests/dummy_data/data/MITE0000000.json")
    e, w = artifact_rules.fasta_affiliation(path=path, ctx=ctx)
    assert w
