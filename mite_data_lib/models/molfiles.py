"""Models for molecular data artifact files"""

from pydantic import BaseModel


class MolInfo(BaseModel):
    """Models info required for mol file artifacts"""

    accession: str
    idx_csv_smarts: str
    idx_csv_smiles: str
    reactionsmarts: str
    substrates: str
    products: str
