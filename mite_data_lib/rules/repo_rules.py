"""Run repo-level rules"""

import re
from pathlib import Path

from mite_data_lib.config.config import settings
from mite_data_lib.models.validation import ValidationIssue


def naming(
    path: Path,
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    e = []
    w = []
    if not re.fullmatch(pattern=settings.mite_pattern, string=path.stem):
        e.append(
            ValidationIssue(
                severity="error",
                location=str(path),
                message=f"Does not follow naming convention.",
            )
        )
    return e, w
