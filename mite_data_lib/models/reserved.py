import json
from datetime import date
from functools import cached_property
from pathlib import Path
from typing import Annotated

import pandas as pd
from pydantic import BaseModel, Field, TypeAdapter, ValidationError

from mite_data_lib.config.config import settings


class ReserveData(BaseModel):
    model_config = dict(extra="forbid", frozen=True)
    by: str
    date: date


ReserveDataAdapter = TypeAdapter(
    dict[Annotated[str, Field(pattern=settings.mite_pattern)], ReserveData]
)


class ReserveService:
    """Load reserved MITE accessions

    Attributes:
        path: path to file
    """

    def __init__(self, path: Path | None = None):
        self.path = path or settings.data.parent / "reserved/reserved_accessions.json"

    @cached_property
    def reserved(self) -> dict[str, ReserveData]:
        try:
            with open(self.path, encoding="utf-8") as f:
                raw = json.load(f)
            return ReserveDataAdapter.validate_python(raw)
        except ValidationError as e:
            raise RuntimeError(
                f"Invalid formatting of reserved MITE accession file: {self.path}"
            ) from e
