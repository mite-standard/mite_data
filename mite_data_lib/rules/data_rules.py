import requests

from mite_data_lib.config.config import settings
from mite_data_lib.models.validation import ValidationContext, ValidationIssue


def status(
    data: dict, ctx: ValidationContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """Correct status for production"""
    e = []
    w = []
    if data.get("status") != "active":
        e.append(
            ValidationIssue(
                severity="error",
                location=data["accession"],
                message="Status is not set to 'active'.",
            )
        )
    return e, w


def reserved(
    data: dict, ctx: ValidationContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """Accession not reserved"""
    e = []
    w = []
    for key, val in ctx.reserved.items():
        if key == data.get("accession"):
            e.append(
                ValidationIssue(
                    severity="error",
                    location=data["accession"],
                    message=f"Accession '{key}' already reserved by {val.by} on {val.date}.",
                )
            )
    return e, w


def duplicate_genpept(
    data: dict, ctx: ValidationContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """GenPept ID not already described by MITE"""
    e = []
    w = []
    if genpept := data["enzyme"]["databaseIds"].get("genpept"):
        df = ctx.proteins
        match = df.loc[df["genpept"] == genpept]
        if not match.empty:
            for i, row in match.iterrows():
                e.append(
                    ValidationIssue(
                        severity="error",
                        location=data["accession"],
                        message=f"Genpept accession '{row['genpept']!s}' already specified in {i!s}",
                    )
                )
    return e, w


def duplicate_uniprot(
    data: dict, ctx: ValidationContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """Uniprot ID not already described by MITE"""
    e = []
    w = []
    if uniprot := data["enzyme"]["databaseIds"].get("uniprot"):
        df = ctx.proteins
        match = df.loc[df["uniprot"] == uniprot]
        if not match.empty:
            for i, row in match.iterrows():
                e.append(
                    ValidationIssue(
                        severity="error",
                        location=data["accession"],
                        message=f"UniProt accession '{row['uniprot']!s}' already specified in {i!s}",
                    )
                )
    return e, w


def uniprot_exists(
    data: dict, ctx: ValidationContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """Uniprot ID can be found in Uniprot repo"""
    e = []
    w = []
    if uniprot := data["enzyme"]["databaseIds"].get("uniprot"):
        if uniprot.startswith("UPI"):
            url = f"https://rest.uniprot.org/uniparc/{uniprot}.fasta"
        else:
            url = f"https://rest.uniprot.org/uniprotkb/{uniprot}.fasta"
        r = requests.head(url=url, timeout=settings.timeout, allow_redirects=True)

        if r.status_code != 200:
            e.append(
                ValidationIssue(
                    severity="error",
                    location=data["accession"],
                    message=f"UniProt accession '{uniprot}' not found on Uniprot server",
                )
            )

    return e, w


def genpept_exists(
    data: dict, ctx: ValidationContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """Uniprot ID can be found in Uniprot repo"""
    e = []
    w = []
    if genpept := data["enzyme"]["databaseIds"].get("genpept"):
        r = requests.head(
            url=f"https://www.ncbi.nlm.nih.gov/protein/{genpept}",
            timeout=settings.timeout,
            allow_redirects=False,
        )
        if r.status_code != 200:
            e.append(
                ValidationIssue(
                    severity="error",
                    location=data["accession"],
                    message=f"NCBI Genpept accession '{genpept}' not found on NCBI server",
                )
            )

    return e, w


def wikidata_exists(
    data: dict, ctx: ValidationContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """Wikidata ID can be found in Wikidata"""


def ids_matching(
    data: dict, ctx: ValidationContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """Uniprot ID and Genpept ID match each other (cross-ref)"""


def check_mibig(
    data: dict, ctx: ValidationContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """MIBiG ID valid (mite protein found in protein list)"""


def check_rhea(
    data: dict, ctx: ValidationContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """Check if uniprot ID has associated Rhea IDs (not always correct though)"""


# TODO: db ids are matching (warning
# TODO: mibig check
# TODO: rhea check
