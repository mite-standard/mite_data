from pathlib import Path

import pytest

from mite_data_lib.services.sequence import SequenceService


@pytest.fixture
def sequence() -> SequenceService:
    return SequenceService(
        fasta=Path("tests/dummy_data/fasta/"),
    )


@pytest.mark.download
def test_fetch_ncbi_valid(sequence):
    seq = sequence.fetch_ncbi(acc="AAK83184.1")
    assert seq


@pytest.mark.download
def test_fetch_ncbi_invalid(sequence):
    with pytest.raises(RuntimeError):
        sequence.fetch_ncbi(acc="nonexisting")


@pytest.mark.download
def test_fetch_uniprot_valid(sequence):
    seq = sequence.fetch_uniprot(acc="Q93KW1")
    assert seq


@pytest.mark.download
def test_fetch_uniprot_invalid(sequence):
    with pytest.raises(RuntimeError):
        sequence.fetch_uniprot(acc="nonexisting")


@pytest.mark.download
def test_seq_match_valid(sequence):
    assert sequence.seq_match(genpept="AAK83184.1", uniprot="Q93KW1")


@pytest.mark.download
def test_seq_match_invalid(sequence):
    assert not sequence.seq_match(genpept="AAK83184.1", uniprot="Q93KW5")


@pytest.mark.download
def test_dump_fasta(sequence):
    seq = sequence.fetch_uniprot(acc="Q93KW1")
    sequence.dump_fasta(mite_acc="MITE0000001", acc="Q93KW1", seq=seq)
