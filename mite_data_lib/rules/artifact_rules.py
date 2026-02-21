import logging
from pathlib import Path

from mite_data_lib.config.config import settings
from mite_data_lib.models.validation import ArtifactContext, ValidationIssue

logger = logging.getLogger(__name__)


# TODO: check for status active should already happen in artifact pipeline


def fasta_check(
    path: Path, ctx: ArtifactContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """Ever non-retired mite file has a fasta file and vice versa"""
    e = []
    w = []

    if not ctx.fasta.joinpath(f"{path.stem}.fasta").exists():
        e.append(
            ValidationIssue(
                severity="error",
                location=path.name,
                message=f"Has no accompanying .fasta file in {ctx.fasta }",
            )
        )

    return e, w


# TODO: entry has an accompanying fasta
# todo: header mite header matches the one in fasta
# todo: every fasta has a mite that is not retired


# interface: every function accepts path, gets context (where does the repo live, for testability)
# reports checks as validation issues
