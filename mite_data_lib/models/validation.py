from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol

import pandas as pd

from mite_data_lib.models.reserved import ReserveData


@dataclass(frozen=True)
class ValidationContext:
    """Stores prepared artifact data for access"""

    reserved: dict[str, ReserveData]
    proteins: pd.DataFrame


@dataclass
class ValidationIssue:
    """Store location and description of issue"""

    severity: Literal["error", "warning"]
    message: str
    location: str | None


class RepoRule(Protocol):
    def __call__(
        self,
        path: Path,
    ) -> tuple[list[ValidationIssue], list[ValidationIssue]]: ...


class DataRule(Protocol):
    def __call__(
        self, data: dict, ctx: ValidationContext
    ) -> tuple[list[ValidationIssue], list[ValidationIssue]]: ...
