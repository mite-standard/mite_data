from pydantic import BaseModel


class MolInfo(BaseModel):
    accession: str
    idx_csv_smarts: str
    idx_csv_smiles: str
    reactionsmarts: str
    substrates: str
    products: str
