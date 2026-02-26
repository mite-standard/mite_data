"""Rules to validate repo for release"""

import json
from hashlib import sha256

from mite_extras import MiteParser
from mite_schema import SchemaManager

from mite_data_lib.config.filenames import names
from mite_data_lib.models.metadata import ArtifactMetadata
from mite_data_lib.models.validation import ArtifactContext, ValidationIssue


def entry_check(
    ctx: ArtifactContext, meta: ArtifactMetadata
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """For each entry, check if it passes mite_extras validation"""
    e = []
    w = []

    model = SchemaManager()

    for entry in ctx.data.glob("MITE*.json"):
        parser = MiteParser()
        try:
            parser.parse_mite_json(json.loads(entry.read_text()))
            model.validate_mite(parser.to_json())
        except Exception as error:
            e.append(
                ValidationIssue(
                    severity="error",
                    location=entry.stem,
                    message=f"MITE entry {entry.name} failed validation: {error!s}",
                )
            )

    return e, w


def fasta_check(
    ctx: ArtifactContext, meta: ArtifactMetadata
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """For each mite entry, check if fasta exists (and vice versa) and if header matches"""
    e = []
    w = []

    for entry in ctx.data.glob("MITE*.json"):
        data = json.loads(entry.read_text())

        db_ids = [data["enzyme"]["databaseIds"].get(i) for i in ("genpept", "uniprot")]

        fasta_path = ctx.fasta.joinpath(f"{data['accession']}.fasta")

        if data["status"] != "active":
            if fasta_path.exists():
                e.append(
                    ValidationIssue(
                        severity="error",
                        location=data["accession"],
                        message=f"Entry retired but still has an accompanying fasta file - investigate!",
                    )
                )
            continue

        if not fasta_path.exists():
            e.append(
                ValidationIssue(
                    severity="error",
                    location=data["accession"],
                    message=f"Has no accompanying .fasta file in {ctx.fasta}",
                )
            )
            continue

        fasta_text = fasta_path.read_text()
        if fasta_text.split()[0].removeprefix(">") != data["accession"]:
            e.append(
                ValidationIssue(
                    severity="error",
                    location=data["accession"],
                    message=f"Mismatch in MITE accession in header of .fasta file {fasta_path}",
                )
            )

        if not fasta_text.split()[1] in db_ids:
            e.append(
                ValidationIssue(
                    severity="error",
                    location=data["accession"],
                    message=f"Mismatch in protein accession in header of .fasta file {fasta_path}",
                )
            )

    for entry in ctx.fasta.glob("MITE*.fasta"):
        if not ctx.data.joinpath(f"{entry.stem}.json").exists():
            e.append(
                ValidationIssue(
                    severity="error",
                    location=entry.stem,
                    message=f"Fasta-file {entry} has no corresponding MITE file - investigate!",
                )
            )

    return e, w


def prot_acc_check(
    ctx: ArtifactContext, meta: ArtifactMetadata
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """Validate hash of mite prot acc file"""

    e = []
    w = []

    path = ctx.metadata / names.prot_acc
    if meta.hash_mite_prot_acc != sha256(path.read_text().encode("utf-8")).hexdigest():
        e.append(
            ValidationIssue(
                severity="error",
                location="mite_prot_accessions.csv",
                message=f"Hash compromised - was the file meddled with?",
            )
        )

    return e, w


def molfiles_check(
    ctx: ArtifactContext, meta: ArtifactMetadata
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """Validate hashes of molfiles"""

    def _format_error(filename: str):
        return ValidationIssue(
            severity="error",
            location=filename,
            message=f"Hash compromised - was the file meddled with?",
        )

    e = []
    w = []

    smarts = ctx.metadata / names.smarts
    if meta.smarts != sha256(smarts.read_text().encode("utf-8")).hexdigest():
        e.append(_format_error("dump_smarts.csv"))

    smiles = ctx.metadata / names.smiles
    if meta.smiles != sha256(smiles.read_text().encode("utf-8")).hexdigest():
        e.append(_format_error("dump_smiles.csv"))

    return e, w


def summary_check(
    ctx: ArtifactContext, meta: ArtifactMetadata
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """Validate hashes of summary files"""

    def _hash_from_json(payload: dict) -> str:
        json_str = json.dumps(
            payload, indent=2, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return sha256(json_str.encode("utf-8")).hexdigest()

    def _format_error(filename: str):
        return ValidationIssue(
            severity="error",
            location=filename,
            message=f"Hash compromised - was the file meddled with?",
        )

    e = []
    w = []

    summary_json = ctx.metadata / names.summary_json
    with open(summary_json) as f:
        data = json.load(f)
    if meta.hash_general_summary != _hash_from_json(data):
        e.append(_format_error("metadata_general.json"))

    summary_mibig = ctx.metadata / names.summary_mibig
    with open(summary_mibig) as f:
        data = json.load(f)
    if meta.hash_mibig_summary != _hash_from_json(data):
        e.append(_format_error("metadata_mibig.json"))

    summary = ctx.metadata / names.summary_csv
    if meta.summary != sha256(summary.read_text().encode("utf-8")).hexdigest():
        e.append(_format_error("summary.csv"))

    return e, w
