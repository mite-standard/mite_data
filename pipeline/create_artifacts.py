import logging
import sys
from pathlib import Path

from mite_data_lib.config.config import settings
from mite_data_lib.config.logging import setup_logger
from mite_data_lib.models.validation import ArtifactContext

logger = logging.getLogger(__name__)


class CreateArtifactRunner:
    """Hold artifact creation pipeline"""

    @staticmethod
    def run(path: Path, ctx: ArtifactContext):
        """Create artifacts from entry"""

        # open file
        # steps depending on services (e.g. Sequence)

        # create fasta entry


def main(entries: list[str], ctx: ArtifactContext) -> None:
    """Run artifact generation

    Args:
        entries: a list of MITE entry filepaths
        ctx: a ArtifactContext object

    Raises:
        RuntimeError: creation failed
    """
    if not entries:
        raise RuntimeError("No entries specified - abort.")

    runner = CreateArtifactRunner()

    for f in entries:
        p = Path(f)
        if not p.exists():
            raise RuntimeError(f"File {p.name} does not exists - abort.")

        runner.run(path=p, ctx=ctx)
        logger.info(f"Created artifacts for {p.name}")


if __name__ == "__main__":
    setup_logger()
    try:
        main(
            entries=sys.argv[1:],
            ctx=ArtifactContext(
                data=settings.data / "data", fasta=settings.data / "fasta"
            ),
        )
        sys.exit(0)
    except Exception as e:
        logger.fatal(f"{e}")
        sys.exit(1)
