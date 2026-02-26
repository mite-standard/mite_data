"""Models for summary file artifacts"""

from pydantic import BaseModel


class SummaryGeneral(BaseModel):
    """Keep track of data parsed for general summary file"""

    accession: str
    status: str
    enzyme_name: str
    enzyme_description: str
    enzyme_ids: dict
    tailoring: str
    reaction_description: str
    cofactors_organic: str
    cofactors_inorganic: str
    organism: str = "Not found"
    domain: str = "Not found"
    kingdom: str = "Not found"
    phylum: str = "Not found"
    class_name: str = "Not found"
    order: str = "Not found"
    family: str = "Not found"


class SummaryMibig(BaseModel):
    """Keep track of data parsed for mibig summary file"""

    mite_accession: str
    mite_url: str
    status: str
    enzyme_name: str
    enzyme_description: str
    enzyme_ids: dict
    enzyme_tailoring: str
    enzyme_refs: list
