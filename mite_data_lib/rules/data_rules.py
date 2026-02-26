"""Rules that MITE data entries need to pass to qualify for merge to main"""

import logging

import requests

from mite_data_lib.config.config import settings
from mite_data_lib.models.validation import ValidationContext, ValidationIssue

logger = logging.getLogger(__name__)


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

    def _build_query(qid: str) -> str:
        return f"""
        ASK {{
            wd:{qid} ?p ?o
        }}
        """

    def _fetch_result(query: str) -> str | bool:
        response = requests.get(
            "https://query.wikidata.org/sparql",
            params={"query": query},
            headers={
                "User-Agent": f"mite_data_bot/0.0 (https://github.com/mite_standard/mite_data; {settings.email})",
                "Accept": "application/sparql-results+json",
            },
            timeout=settings.timeout,
        )
        response.raise_for_status()

        rsps = response.json()
        return rsps.get("boolean")

    e = []
    w = []
    if wikidata := data["enzyme"]["databaseIds"].get("wikidata"):
        if not _fetch_result(query=_build_query(qid=wikidata)):
            e.append(
                ValidationIssue(
                    severity="error",
                    location=data["accession"],
                    message=f"Wikidata ID '{wikidata}' not found or has no statements",
                )
            )

    return e, w


def mibig_exists(
    data: dict, ctx: ValidationContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """MIBiG ID valid (mite protein found in protein list)"""
    e = []
    w = []

    if mibig := data["enzyme"]["databaseIds"].get("mibig"):
        if mibig not in ctx.mibig_proteins:
            e.append(
                ValidationIssue(
                    severity="error",
                    location=data["accession"],
                    message=f"MIBIG ID '{mibig}' does not exist in MIBiG v {settings.mibig_version}",
                )
            )

    return e, w


def ids_matching(
    data: dict, ctx: ValidationContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """Uniprot ID and Genpept ID point to identical protein sequence"""
    e = []
    w = []

    uniprot = data["enzyme"]["databaseIds"].get("uniprot")
    genpept = data["enzyme"]["databaseIds"].get("genpept")

    if uniprot and genpept:
        if not ctx.seq_service.seq_match(uniprot=uniprot, genpept=genpept):
            e.append(
                ValidationIssue(
                    severity="error",
                    location=data["accession"],
                    message=f"Uniprot ID '{uniprot}' and GenPept ID '{genpept}' resolve to different protein sequences - investigate!",
                )
            )

    return e, w


def check_mibig_protein(
    data: dict, ctx: ValidationContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """MIBiG ID valid (mite protein found in protein list)"""
    e = []
    w = []

    genpept = data["enzyme"]["databaseIds"].get("genpept")
    mibig = data["enzyme"]["databaseIds"].get("mibig")

    if genpept and mibig:
        if not genpept in ctx.mibig_proteins.get(mibig, []):
            e.append(
                ValidationIssue(
                    severity="error",
                    location=data["accession"],
                    message=f"GenPept ID '{genpept}' not found in MIBiG v {settings.mibig_version} entry '{mibig}' - investigate!",
                )
            )

    return e, w


def check_rhea(
    data: dict, ctx: ValidationContext
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    """Check if uniprot ID has associated Rhea IDs (not always correct though)"""

    def _fetch(acc: str) -> requests.Response:
        return requests.get(
            url="https://www.rhea-db.org/rhea?",
            params={
                "query": acc,
                "columns": "rhea-id",
                "format": "tsv",
                "limit": 10,
            },
            timeout=settings.timeout,
        )

    e = []
    w = []

    if uniprot := data["enzyme"]["databaseIds"].get("uniprot"):
        known_rhea = set()
        for reaction in data["reactions"]:
            if val := reaction.get("databaseIds", {}).get("rhea"):
                known_rhea.add(val)

        try:
            response = _fetch(uniprot)
            response.raise_for_status()
        except requests.exceptions.ConnectTimeout:
            logger.warning(f"Warning: could not connect to Rhea: Timeout")
            return e, w
        except requests.HTTPError:
            logger.warning(f"Warning: connecting to Rhea lead to HttpError")
            return e, w

        if response.status_code == 200:
            retrieved_rhea = {
                i.removeprefix("RHEA:") for i in response.text.split()[2:]
            }

            diff = sorted(retrieved_rhea.difference(known_rhea))
            for rhea in diff:
                w.append(
                    ValidationIssue(
                        severity="error",
                        location=data["accession"],
                        message=f"UniProt ID '{uniprot}' associated to Rhea entry '{rhea}' but not mentioned in MITE entry. Should it be added?",
                    )
                )

    return e, w
