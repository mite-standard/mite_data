import json
from functools import cached_property
from pathlib import Path

from pydantic import ValidationError

from mite_data_lib.config.config import settings
from mite_data_lib.models.reserved import ReserveData, ReserveDataAdapter


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
