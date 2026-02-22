import concurrent.futures
import logging
from pathlib import Path
from typing import Annotated

import requests
from Bio import Entrez, SeqIO
from pydantic import BaseModel, Field, TypeAdapter

from mite_data_lib.config.config import settings
from mite_data_lib.config.filenames import names
from mite_data_lib.models.summary import SummaryGeneral, SummaryMibig

logger = logging.getLogger(__name__)
Entrez.email = settings.email

# parse files into single json/csv/ or mibig json

# similar to prot_acc
# have build method, dump method
# have a way to update the entries
# also have them sorted

# get taxonomy from first uniprot and if no match, ncbi


class TaxonomyResolver:
    def resolve(self, model: SummaryGeneral) -> SummaryGeneral:
        if uniprot := model.enzyme_ids.get("uniprot"):
            try:
                content = self.fetch_uniprot(uniprot)
                record = content.get("organism", {}).get("lineage")
                if not record:
                    raise ValueError("Missing lineage")

                return model.model_copy(
                    update={
                        "domain": self.list_get(record, 0),
                        "kingdom": self.list_get(record, 1),
                        "phylum": self.list_get(record, 2),
                        "class_name": self.list_get(record, 3),
                        "order": self.list_get(record, 4),
                        "family": self.list_get(record, 5),
                        "organism": content.get("organism", {}).get(
                            "scientificName", "Not found"
                        ),
                    }
                )
            except Exception as e:
                logger.warning(f"Uniprot taxonomy info download failed: {e!s}")
                logger.warning(f"Retry with NCBI")

        if genpept := model.enzyme_ids.get("genpept"):
            try:
                organism, taxonomy = self.fetch_ncbi(genpept)
                if not taxonomy:
                    raise ValueError("Missing lineage")

                return model.model_copy(
                    update={
                        "domain": self.list_get(taxonomy, 0),
                        "kingdom": self.list_get(taxonomy, 1),
                        "phylum": self.list_get(taxonomy, 2),
                        "class_name": self.list_get(taxonomy, 3),
                        "order": self.list_get(taxonomy, 4),
                        "family": self.list_get(taxonomy, 5),
                        "organism": organism,
                    }
                )
            except Exception as e:
                logger.warning(f"NCBI taxonomy info download failed: {e!s}")

        logger.warning(f"{model.accession}: could not download taxonomy information")

        return model

    @staticmethod
    def list_get(l: list, idx: int) -> str:
        try:
            return l[idx]
        except IndexError:
            return "Not found"

    @staticmethod
    def fetch_uniprot(acc: str) -> dict:
        """Get taxonomy info from uniprot"""

        def _service(uniprot: str) -> str:
            if uniprot.startswith("UPI"):
                return f"https://rest.uniprot.org/uniparc/{uniprot}.json"
            else:
                return f"https://rest.uniprot.org/uniprotkb/{uniprot}.json"

        response = requests.get(_service(acc), timeout=settings.timeout)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def fetch_ncbi(acc: str) -> tuple[str, list]:
        """Get taxonomy info from ncbi

        Raises:
            RuntimeError: Timeout of call

        """

        def _fetch(ncbi: str):
            handle = Entrez.efetch(db="protein", id=ncbi, rettype="gb", retmode="text")
            record = SeqIO.read(handle, "genbank")
            organism = record.annotations.get("organism", "Not found")
            taxonomy = record.annotations.get("taxonomy", [])
            handle.close()
            return organism, taxonomy

        with concurrent.futures.ThreadPoolExecutor() as ex:
            future = ex.submit(_fetch, acc)
            try:
                return future.result(timeout=settings.timeout)
            except concurrent.futures.TimeoutError as e:
                raise RuntimeError("Warning: could not connect to NCBI: Timeout") from e


class SummaryParser:
    def parse_general(self, data: dict) -> SummaryGeneral:
        cofactors_organic = "N/A"
        if val := data["enzyme"].get("cofactors", {}).get("organic", []):
            cofactors_organic = "|".join(sorted(set(val)))

        cofactors_inorganic = "N/A"
        if val := data["enzyme"].get("cofactors", {}).get("inorganic", []):
            cofactors_inorganic = "|".join(sorted(set(val)))

        return SummaryGeneral(
            accession=data["accession"],
            status=data["status"],
            enzyme_name=data["enzyme"]["name"],
            enzyme_description=data["enzyme"].get("description", "N/A"),
            enzyme_ids=data["enzyme"]["databaseIds"],
            tailoring=self.get_tailoring(data),
            reaction_description=data.get("reactions")[0].get("description", "N/A"),
            cofactors_organic=cofactors_organic,
            cofactors_inorganic=cofactors_inorganic,
        )

    def parse_mibig(self, data: dict) -> SummaryMibig | None:
        mibig = data["enzyme"]["databaseIds"].get("mibig")
        if not mibig:
            return

        genpept = data["enzyme"]["databaseIds"].get("genpept")
        if not genpept:
            return

        return SummaryMibig(
            mite_accession=data["accession"],
            mite_url=f"https://bioregistry.io/mite:{data['accession']}",
            status=data["status"],
            enzyme_name=data["enzyme"]["name"],
            enzyme_description=data["enzyme"].get("description", "N/A"),
            enzyme_ids=data["enzyme"]["databaseIds"],
            enzyme_tailoring=self.get_tailoring(data),
            enzyme_refs=data["enzyme"]["references"],
        )

    @staticmethod
    def get_tailoring(data: dict) -> str:
        return (
            "|".join(
                sorted(
                    {
                        tailoring
                        for reaction in data.get("reactions", [])
                        for tailoring in reaction.get("tailoring", [])
                    }
                )
            )
            or "N/A"
        )


class SummaryMibigStore:
    entries: TypeAdapter[
        dict[Annotated[str, Field(pattern=settings.mibig_pattern)], list[SummaryMibig]]
    ]

    def upsert(self):
        # todo: implement updating
        pass

    def write_to_json(self):
        # todo: implement writing
        pass


class SummaryGeneralStore:
    def __init__(self, path: Path):
        self.path = path
        self.entries: dict[str, SummaryGeneral] = {}

    def upsert(self):
        # todo: implement updating
        pass

    def write_to_json(self):
        # todo: implement formatting and writing
        pass

    def write_to_csv(self):
        # todo: implement formatting and writing
        pass


class SummaryService:
    """Creates summary artifact data

    Attributes:
        data: Path to data dir
        dump: Path to artifact dump dir

    """

    def __init__(self, data: Path, dump: Path):
        self.data = data
        self.dump = dump

    def update_from_entry(self, path: Path):
        # todo: implement logic
        # ensure files exist
        # load files
        # check version
        # check entry exists
        # parse data

        pass

    def _ensure_files(self):
        pass

    def _build(self):
        pass

    # todo: implement other helper methods

    @staticmethod
    def _load_json(path: Path) -> dict:
        pass
