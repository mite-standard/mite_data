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
                    message=f"Accession {key} already reserved by {val.by} on {val.date}.",
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
                        message=f"Genpept accession {row['genpept']!s} already specified in {i!s}",
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
                        message=f"UniProt accession {row['uniprot']!s} already specified in {i!s}",
                    )
                )
    return e, w


# TODO: not already in protein accessions/duplicate (error
# TODO: db ids are matching (warning
# TODO: mibig check
# TODO: rhea check
