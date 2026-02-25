from pydantic import BaseModel


class ArtifactMetadata(BaseModel):
    """Metadata for derived artifacts

    Attributes:
        version: MITE version (semantic)
        hash_mite_prot_acc: hash of mite_prot_accessions.csv
        hash_general_summary: hash of metadata_general.json
        hash_mibig_summary: hash of metadata_mibig.json
        smarts: hash of dump_smarts.csv
        smiles: hash of dump_smiles.csv
        product: hash of product_list.pickle
        reaction: hash of reaction_fps.pickle
        substrate: hash of substrate_list.pickle
        summary: hash of summary.csv
    """

    version: str
    hash_mite_prot_acc: str | None = None
    hash_general_summary: str | None = None
    hash_mibig_summary: str | None = None
    smarts: str | None = None
    smiles: str | None = None
    product: str | None = None
    reaction: str | None = None
    substrate: str | None = None
    summary: str | None = None
