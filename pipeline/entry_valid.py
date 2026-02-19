import json
import logging
import sys
from pathlib import Path

from mite_extras import MiteParser
from mite_schema import SchemaManager

from mite_data_lib.models.reserved import ReserveService
from mite_data_lib.models.validation import DataRule, ValidationContext, ValidationIssue
from mite_data_lib.rules import data_rules, repo_rules
from mite_data_lib.services.prot_accessions import ProtAccessionService

logger = logging.getLogger(__name__)

REPO_RULES = [
    repo_rules.naming,
]

DATA_RULES: list[DataRule] = [
    data_rules.status,
    data_rules.reserved,
    data_rules.duplicate_genpept,
    data_rules.duplicate_uniprot,
]


class EntryValidRunner:
    """Runs validation suite on entry"""

    def run(
        self, path: Path, ctx: ValidationContext
    ) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
        """Validate a single entry file"""

        data = self._load_and_validate_schema(path)
        errors = []
        warnings = []

        for rule in REPO_RULES:
            e, w = rule(path=path)
            errors.extend(e)
            warnings.extend(w)

        for rule in DATA_RULES:
            e, w = rule(data=data, ctx=ctx)
            errors.extend(e)
            warnings.extend(w)

        return errors, warnings

    @staticmethod
    def _load_and_validate_schema(path: Path) -> dict:
        if not path.exists():
            raise FileNotFoundError(f"Could not find file {path}")

        with open(path) as f:
            data = json.load(f)

        try:
            parser = MiteParser()
            parser.parse_mite_json(data=data)
            SchemaManager().validate_mite(instance=parser.to_json())
            return data
        except Exception as e:
            raise RuntimeError(f"File {path} failed validation: {e!s}.") from e


def main(
    entries: list[str] | None = None, ctx: ValidationContext | None = None
) -> None:
    """Run validation functions on MITE entries

    Args:
        entries: a list of MITE entry filepaths
        ctx: a ValidationContext object

    Raises:
        RuntimeError: validation failed
    """

    runner = EntryValidRunner()

    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    if not entries:
        RuntimeError("No entries specified - abort.")

    for f in entries:
        p = Path(f)
        if not p.exists():
            RuntimeError(f"File {p.name} does not exists - abort.")

        e, w = runner.run(path=p, ctx=ctx)
        errors.extend(e)
        warnings.extend(w)

    if warnings:
        logger.warning(f"Entry validation found {len(warnings)} warnings.")
        for w in warnings:
            logger.warning(f"{w.severity} - {w.location} - {w.message}")

    if errors:
        m = f"Entry validation found {len(errors)} errors."
        logger.fatal(m)
        for e in errors:
            logger.fatal(f"{e.severity} - {e.location} - {e.message}")
        raise RuntimeError


if __name__ == "__main__":
    try:
        main(
            entries=sys.argv[1:],
            ctx=ValidationContext(
                reserved=ReserveService().reserved,
                proteins=ProtAccessionService().proteins,
            ),
        )
        sys.exit(0)
    except Exception as error:
        logger.fatal(f"{error!s}")
        sys.exit(1)
