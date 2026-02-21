import json
import logging
import sys
from pathlib import Path

from mite_data_lib.config.config import settings
from mite_data_lib.config.logging import setup_logger
from mite_data_lib.models.validation import ArtifactContext, FastaRule, ValidationIssue
from mite_data_lib.rules import fasta_rules

logger = logging.getLogger(__name__)

FASTA_RULE: list[FastaRule] = [
    fasta_rules.fasta_check,
]

# todo: check prot_acc
# todo: check metadata
# todo: check molfiles
# todo: check summary


class ValidateArtifactRunner:
    """Runs validation suite on artifacts"""

    @staticmethod
    def run(
        path: Path, ctx: ArtifactContext
    ) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
        """Validate a single entry file"""

        errors = []
        warnings = []

        with open(path) as f:
            data = json.load(f)

        for rule in FASTA_RULE:
            e, w = rule(data=data, ctx=ctx)
            errors.extend(e)
            warnings.extend(w)

        # TODO: add artifact rules for integrity checks

        return errors, warnings


def main(entries: list[str], ctx: ArtifactContext) -> None:
    """Run artifact generation checks

    Args:
        entries: a list of MITE entry filepaths
        ctx: a ArtifactContext object

    Raises:
        RuntimeError: validation failed
    """

    logger.info("Artifact validation started")

    runner = ValidateArtifactRunner()

    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    if not entries:
        raise RuntimeError("No entries specified - abort.")

    for f in entries:
        p = Path(f)
        if not p.exists():
            raise RuntimeError(f"File {p.name} does not exists - abort.")

        e, w = runner.run(path=p, ctx=ctx)
        errors.extend(e)
        warnings.extend(w)

    if warnings:
        logger.warning(f"Artifact validation found {len(warnings)} warnings.")
        for w in warnings:
            logger.warning(f"{w.severity} - {w.location} - {w.message}")

    if errors:
        m = f"Artifact validation found {len(errors)} errors."
        logger.critical(m)
        for e in errors:
            logger.critical(f"{e.severity} - {e.location} - {e.message}")
        raise RuntimeError("One or more validation errors occurred - abort")

    logger.info("Artifact validation completed")


if __name__ == "__main__":
    setup_logger()
    try:
        main(
            entries=sys.argv[1:],
            ctx=ArtifactContext(
                fasta=settings.data / "fasta",
                data=settings.data / "data",
                metadata=settings.data / "metadata",
            ),
        )
        sys.exit(0)
    except Exception as error:
        logger.critical(f"{error!s}")
        sys.exit(1)
