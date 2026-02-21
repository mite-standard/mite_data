import json
import logging
from pathlib import Path

from mite_data_lib.models.validation import ArtifactContext, ValidationIssue

logger = logging.getLogger(__name__)


def fasta_check(
    data: dict, ctx: ArtifactContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """For mite entry, check if fasta exists and if header matches"""
    e = []
    w = []

    fasta_path = ctx.fasta.joinpath(f"{data["accession"]}.fasta")

    if data["status"] != "active":
        if fasta_path.exists():
            e.append(
                ValidationIssue(
                    severity="error",
                    location=data["accession"],
                    message=f"Entry retired but still has an accompanying fasta file - remove it!.",
                )
            )
        return e, w

    if not fasta_path.exists():
        e.append(
            ValidationIssue(
                severity="error",
                location=data["accession"],
                message=f"Has no accompanying .fasta file in {ctx.fasta}",
            )
        )
        return e, w

    db_ids = [data["enzyme"]["databaseIds"].get(i) for i in ("genpept", "uniprot")]
    with open(fasta_path) as f:
        fasta = f.read()

    mite_acc = fasta.split()[0].removeprefix(">")
    if mite_acc != data["accession"]:
        e.append(
            ValidationIssue(
                severity="error",
                location=data["accession"],
                message=f"Mismatch in MITE accession in header of .fasta file {fasta_path}",
            )
        )

    prot_acc = fasta.split()[1]
    if not prot_acc in db_ids:
        e.append(
            ValidationIssue(
                severity="error",
                location=data["accession"],
                message=f"Mismatch in protein accession in header of .fasta file {fasta_path}",
            )
        )

    return e, w
