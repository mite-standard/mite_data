from pydantic import BaseModel


class ArtifactMetadata(BaseModel):
    """Metadata for derived artifacts

    Attributes:
        version: MITE version (semantic)

    """

    version: str
    hash_mite_prot_acc: str | None = None

    # TODO: update for the required data
