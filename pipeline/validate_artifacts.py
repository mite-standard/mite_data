import json
import logging
import sys
from pathlib import Path

from mite_data_lib.config.config import settings
from mite_data_lib.config.logging import setup_logger
from mite_data_lib.models.metadata import ArtifactMetadata
from mite_data_lib.models.validation import (
    ArtifactContext,
    ReleaseRule,
    ValidationIssue,
)
from mite_data_lib.rules import release_rules

logger = logging.getLogger(__name__)


RELEASE_RULES: list[ReleaseRule] = [
    release_rules.fasta_check,
    release_rules.prot_acc_check,
    release_rules.molfiles_check,
    release_rules.summary_check,
    release_rules.entry_check,
]


class ValidateReleaseRunner:
    """Runs validation suite on artifacts"""

    @staticmethod
    def run(
        ctx: ArtifactContext, meta: ArtifactMetadata
    ) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
        """Validate a single entry file"""

        errors = []
        warnings = []

        for rule in RELEASE_RULES:
            e, w = rule(ctx=ctx, meta=meta)
            errors.extend(e)
            warnings.extend(w)

        return errors, warnings


def main(ctx: ArtifactContext, meta: ArtifactMetadata) -> None:
    """Perform release check by running rules on data and artifacts

    Args:
        ctx: a ArtifactContext object
        meta: a ArtifactMetadata object

    Raises:
        RuntimeError: validation failed
    """

    logger.info("Artifact validation started")

    runner = ValidateReleaseRunner()

    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    e, w = runner.run(ctx=ctx, meta=meta)
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
            ctx=ArtifactContext(
                fasta=settings.data / "fasta",
                data=settings.data / "data",
                metadata=settings.data / "metadata",
            ),
            meta=ArtifactMetadata(
                **json.loads(
                    settings.data.joinpath(
                        "metadata/artifact_metadata.json"
                    ).read_text()
                )
            ),
        )
        sys.exit(0)
    except Exception as error:
        logger.critical(f"{error!s}")
        sys.exit(1)
