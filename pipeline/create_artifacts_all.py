"""Generate artifacts from all MITE entries in the context of release preparation"""

import logging
import sys

from mite_data_lib.config.config import settings
from mite_data_lib.config.logging import setup_logger
from mite_data_lib.models.validation import ArtifactContext
from pipeline.create_artifacts_single import CreateArtifactRunner

logger = logging.getLogger(__name__)


def main(ctx: ArtifactContext) -> None:
    """Run artifact generation for all entries

    Args:
        ctx: a ArtifactContext object

    Raises:
        RuntimeError: creation failed
    """
    logger.info("Started artifact creation")

    runner = CreateArtifactRunner()
    runner.run_all(ctx=ctx)

    logger.info("Completed artifact creation")


if __name__ == "__main__":
    setup_logger()
    try:
        main(
            ctx=ArtifactContext(
                data=settings.data / "data",
                fasta=settings.data / "fasta",
                metadata=settings.data / "metadata",
            ),
        )
        sys.exit(0)
    except Exception as e:
        logger.fatal(f"{e}")
        sys.exit(1)
