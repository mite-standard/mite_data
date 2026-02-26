"""Model to keep track of mibig metadata"""

from typing import Annotated

from pydantic import BaseModel, Field, TypeAdapter

from mite_data_lib.config.config import settings


class MIBiGMetadata(BaseModel):
    """Holds MIBiG metadata

    Attributes:
        version: MIBiG semantic versioning
        record: URL to Zenodo record of version
        hash: a sha_256 hash to verify integrity
    """

    version: str
    record: str
    hash: str


MIBiGDataAdapter = TypeAdapter(
    dict[Annotated[str, Field(pattern=settings.mibig_pattern)], list[str]]
)
