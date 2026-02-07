from pydantic import BaseModel


class MIBiGMetadata(BaseModel):
    """Reads MIBiG metadata file

    Attributes:
        version: MIBiG semantic versioning
        record: URL to Zenodo record of version
    """

    version: str
    record: str
