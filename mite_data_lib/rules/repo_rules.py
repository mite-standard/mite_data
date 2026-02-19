import re
from pathlib import Path

from mite_data_lib.config.config import settings
from mite_data_lib.models.validation import ValidationIssue


def naming(
    path: Path, pattern: None | re.Pattern = settings.mite_pattern
) -> tuple[list[str], list[str]]:
    e = []
    w = []
    if not re.fullmatch(pattern=pattern, string=path.stem):
        e.append(f"Does not follow naming convention: {path.stem}.")
    return e, w
