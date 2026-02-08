from mite_data_lib.models.validation import ReserveService


def status(data: dict) -> tuple[list[str], list[str]]:
    e = []
    w = []
    if data.get("status") != "active":
        e.append(f"Status is not set to 'active'.")
    return e, w


def accession(data: dict) -> tuple[list[str], list[str]]:
    e = []
    w = []
    for key, val in ReserveService().reserved.items():
        if key == data.get("accession"):
            e.append(f"Accession {key} already reserved by {val.by} on {val.date}.")
    return e, w


# not already in protein accessions/duplicate (error
# db ids are matching (warning
# mibig check
# rhea check
