from typing import Annotated

from pydantic import BaseModel, Field, TypeAdapter

from mite_data_lib.config.config import settings


class MIBiGMetadata(BaseModel):
    """Holds MIBiG metadata

    Attributes:
        version: MIBiG semantic versioning
        record: URL to Zenodo record of version
    """

    version: str
    record: str


class MIBiGProtData(BaseModel):
    """Holds MIBiG protein information"""

    model_config = dict(extra="forbid", frozen=True)
    proteins: tuple[str]


MIBiGDataAdapter = TypeAdapter(
    dict[Annotated[str, Field(pattern=settings.mibig_pattern)], list[str]]
)
