def status(data: dict) -> tuple[list[str], list[str]]:
    e = []
    w = []
    if data.get("status") != "active":
        e.append(f"Status is not set to 'active'.")
    return e, w


# accessoin not 9999 error
# not already in protein accessions/duplicate (error
# db ids are matching (warning
# mibig check
# rhea check
