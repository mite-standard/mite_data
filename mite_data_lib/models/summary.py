from pydantic import BaseModel


class SummaryGeneral(BaseModel):
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
    mite_accession: str
    mite_url: str
    status: str
    enzyme_name: str
    enzyme_description: str
    enzyme_ids: dict
    enzyme_tailoring: str
    enzyme_refs: list
