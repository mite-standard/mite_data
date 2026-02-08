import json
from functools import cached_property
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, TypeAdapter, ValidationError

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
    proteins: list[str]


MIBiGDataAdapter = TypeAdapter(
    dict[Annotated[str, Field(pattern=settings.mibig_pattern)], list[str]]
)


class MIBiGProtService:
    """Load and cache the MIBiG proteins

    Attribute:
        path: path to file
    """

    def __init__(self, path: Path | None = None):
        self.path = path or settings.data / "mibig/mibig_proteins.json"

    @cached_property
    def mibig_proteins(self) -> dict[str, list]:
        try:
            with open(self.path) as f:
                raw = json.load(f)
            return MIBiGDataAdapter.validate_python(raw)
        except ValidationError as e:
            raise RuntimeError(
                f"Invalid formatting of MIBIG proteins file: {self.path}"
            ) from e
