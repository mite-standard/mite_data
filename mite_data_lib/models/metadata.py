from pydantic import BaseModel


class ArtifactMetadata(BaseModel):
    """Metadata for derived artifacts

    Attributes:
        version: MITE version (semantic)

    """

    version: str
    hash_mite_prot_acc: str | None = None
    hash_general_summary: str | None = None
    hash_mibig_summary: str | None = None
