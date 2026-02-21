from pathlib import Path

from mite_data_lib.models.validation import ArtifactContext
from pipeline.validate_artifacts import main


def test_main_valid():
    entries = ["tests/dummy_data/data/MITE0000000.json"]
    ctx = ArtifactContext(
        fasta=Path("tests/dummy_data/fasta/"),
        data=Path("tests/dummy_data/data/"),
        metadata=Path("tests/dummy_data/metadata/"),
    )
    assert main(entries=entries, ctx=ctx) is None
