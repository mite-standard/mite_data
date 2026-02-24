import json
import logging
import sys
from importlib.metadata import metadata
from pathlib import Path

from mite_data_lib.config.config import settings
from mite_data_lib.config.logging import setup_logger
from mite_data_lib.models.validation import ArtifactContext
from mite_data_lib.services.molfiles import MolInfoService
from mite_data_lib.services.prot_accessions import ProtAccessionService
from mite_data_lib.services.sequence import SequenceService
from mite_data_lib.services.summary import SummaryService

logger = logging.getLogger(__name__)


class CreateArtifactRunner:
    """Hold artifact creation pipeline"""

    def run(self, path: Path, ctx: ArtifactContext) -> None:
        """Create artifacts from entry"""

        logger.info(f"Started artifact creation for '{path.name}'")

        with open(path) as f:
            data = json.load(f)

        self.create_fasta(data=data, ctx=ctx)
        self.create_protein_acc(path=path, ctx=ctx)
        self.create_summary(path=path, ctx=ctx)
        self.create_molfiles(ctx=ctx)

        logger.info(f"Completed artifact creation for '{path.name}'")

    @staticmethod
    def create_fasta(data: dict, ctx: ArtifactContext) -> None:
        """Create fasta entry"""

        logger.debug("Started fasta creation")

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

        logger.debug("Completed fasta creation")

    @staticmethod
    def create_protein_acc(path: Path, ctx: ArtifactContext) -> None:
        """Update or create mite protein acc file"""

        logger.debug("Started MITE prot acc updating")

        prot_service = ProtAccessionService(
            data=ctx.data,
            dump=ctx.metadata,
            prot_acc=ctx.metadata / "mite_prot_accessions.csv",
            metadata=ctx.metadata / "artifact_metadata.json",
        )

        prot_service.update_from_entry(path)

        logger.debug("Completed MITE prot acc updating")

    @staticmethod
    def create_molfiles(ctx: ArtifactContext) -> None:
        logger.debug("Started Molfile creation")

        service = MolInfoService(data=ctx.data, dump=ctx.metadata)
        service.create_molfiles()

        logger.debug("Completed MITE prot acc updating")

    @staticmethod
    def create_summary(path: Path, ctx: ArtifactContext) -> None:
        """Update or create summary general json + csv"""

        logger.info(f"Started summary artifact creation for entry '{path.name}'")

        service = SummaryService(data=ctx.data, dump=ctx.metadata)
        service.create_summary_general(path)
        service.create_summary_mibig(path)

        logger.info(
            f"Completed summary artifact creation upsert for entry '{path.name}'"
        )


def main(entries: list[str], ctx: ArtifactContext) -> None:
    """Run artifact generation

    Args:
        entries: a list of MITE entry filepaths
        ctx: a ArtifactContext object

    Raises:
        RuntimeError: creation failed
    """

    logger.info("Started artifact creation")

    runner = CreateArtifactRunner()

    if not entries:
        raise RuntimeError("No entries specified - abort.")

    for f in entries:
        p = Path(f)
        if not p.exists():
            raise RuntimeError(f"File {p.name} does not exists - abort.")
        runner.run(path=p, ctx=ctx)

    logger.info("Completed artifact creation")


if __name__ == "__main__":
    setup_logger()
    try:
        main(
            entries=sys.argv[1:],
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
