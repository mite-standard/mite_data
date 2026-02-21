import json
import logging
import sys
from pathlib import Path

from mite_data_lib.config.config import settings
from mite_data_lib.config.logging import setup_logger
from mite_data_lib.models.validation import ArtifactContext
from mite_data_lib.services.sequence import SequenceService

logger = logging.getLogger(__name__)


class CreateArtifactRunner:
    """Hold artifact creation pipeline"""

    def run(self, path: Path, ctx: ArtifactContext) -> None:
        """Create artifacts from entry"""

        with open(path) as f:
            data = json.load(f)

        self.create_fasta(data=data, ctx=ctx)

    @staticmethod
    def create_fasta(data: dict, ctx: ArtifactContext) -> None:
        """Create fasta entry"""

        logger.debug("Fasta creation started")

        seq_service = SequenceService(fasta=ctx.fasta)

        if uniprot := data["enzyme"]["databaseIds"].get("uniprot"):
            seq_service.dump_fasta(
                mite_acc=data["accession"],
                acc=uniprot,
                seq=seq_service.fetch_uniprot(uniprot),
            )
        elif genpept := data["enzyme"]["databaseIds"].get("genpept"):
            seq_service.dump_fasta(
                mite_acc=data["accession"],
                acc=genpept,
                seq=seq_service.fetch_ncbi(genpept),
            )
        else:
            raise RuntimeError("Fasta download failed: no genpept or uniprot ID")

        logger.debug("Fasta creation completed")

    @staticmethod
    def create_protein_acc(data: dict, ctx: ArtifactContext) -> None:
        pass

    @staticmethod
    def create_metadata(data: dict, ctx: ArtifactContext) -> None:
        pass

    @staticmethod
    def create_molfiles(data: dict, ctx: ArtifactContext) -> None:
        pass

    @staticmethod
    def create_summary(data: dict, ctx: ArtifactContext) -> None:
        pass


def main(entries: list[str], ctx: ArtifactContext) -> None:
    """Run artifact generation

    Args:
        entries: a list of MITE entry filepaths
        ctx: a ArtifactContext object

    Raises:
        RuntimeError: creation failed
    """

    logger.info("Artifact creation started")

    runner = CreateArtifactRunner()

    if not entries:
        raise RuntimeError("No entries specified - abort.")

    for f in entries:
        p = Path(f)
        if not p.exists():
            raise RuntimeError(f"File {p.name} does not exists - abort.")

        runner.run(path=p, ctx=ctx)
        logger.info(f"Created artifacts for {p.name}")

    logger.info("Artifact creation completed")


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
