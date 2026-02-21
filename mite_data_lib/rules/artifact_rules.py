import json
import logging
from pathlib import Path

from mite_data_lib.models.validation import ArtifactContext, ValidationIssue

logger = logging.getLogger(__name__)


# TODO: check for status active should already happen in artifact pipeline


def fasta_check(
    path: Path, ctx: ArtifactContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """Check if fasta header matches data in MITE entry"""
    e = []
    w = []

    with open(path) as f:
        data = json.load(f)

    db_ids = [data["enzyme"]["databaseIds"].get(i) for i in ("genpept", "uniprot")]

    fasta_path = ctx.fasta.joinpath(f"{path.stem}.fasta")
    if not fasta_path.exists():
        e.append(
            ValidationIssue(
                severity="error",
                location=path.name,
                message=f"Has no accompanying .fasta file in {ctx.fasta}",
            )
        )
        return e, w

    with open(fasta_path) as f:
        fasta = f.read()

    mite_acc = fasta.split()[0].removeprefix(">")
    if mite_acc != path.stem:
        e.append(
            ValidationIssue(
                severity="error",
                location=path.name,
                message=f"Mismatch in MITE accession in header of .fasta file {fasta_path}",
            )
        )

    prot_acc = fasta.split()[1]
    if not prot_acc in db_ids:
        e.append(
            ValidationIssue(
                severity="error",
                location=path.name,
                message=f"Mismatch in protein accession in header of .fasta file {fasta_path}",
            )
        )

    return e, w


def fasta_affiliation(
    path: Path, ctx: ArtifactContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """Check if fasta header matches data in MITE entry"""
    e = []
    w = []

    for fasta in sorted(ctx.fasta.glob("*.fasta")):
        acc = Path(fasta).stem
        if not ctx.data.joinpath(f"{acc}.json").exists():
            w.append(
                ValidationIssue(
                    severity="warning",
                    location=path.name,
                    message=f"Fasta file '{fasta}' is missing a MITE entry: investigate!",
                )
            )

    return e, w
