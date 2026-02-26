"""Models for keeping track of reserved MITE accessions"""

from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, TypeAdapter

from mite_data_lib.config.config import settings


class ReserveData(BaseModel):
    model_config = dict(extra="forbid", frozen=True)
    by: str
    date: date


ReserveDataAdapter = TypeAdapter(
    dict[Annotated[str, Field(pattern=settings.mite_pattern)], ReserveData]
)
