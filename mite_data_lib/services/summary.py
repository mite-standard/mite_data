import concurrent.futures
import json
import logging
from hashlib import sha256
from pathlib import Path

import pandas as pd
import requests
from Bio import Entrez, SeqIO

from mite_data_lib.config.config import settings
from mite_data_lib.config.filenames import names
from mite_data_lib.models.metadata import ArtifactMetadata
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
    """Resolve DB accessions into taxonomy information"""

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
    """Parse MITE entries into objects"""

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
    def __init__(self, data: Path, dump: Path):
        self.data = data
        self.dump = dump
        self.entries: dict[str, SummaryMibig] = {}

        self.meta_artifact = dump / names.meta_artifact
        self.summary_mibig = dump / names.summary_mibig

    def load(self):
        """Load existing mibig metadata"""

        def _upsert_all():
            logger.warning(
                f"{self.summary_mibig}: file not found or compromised hash - re-create all entries"
            )
            for entry in self.data.glob("MITE*.json"):
                self.upsert(entry)

        if not self.summary_mibig.exists():
            _upsert_all()
            return

        raw = json.loads(self.summary_mibig.read_text())
        if self._validate_hash(raw):
            for _k, v in raw["entries"].items():
                for e in v:
                    self.entries[e["mite_accession"]] = SummaryMibig.model_validate(e)
        else:
            _upsert_all()

    def _validate_hash(self, raw: dict) -> bool:
        model = ArtifactMetadata(**json.loads(self.meta_artifact.read_text()))
        if not model.hash_mibig_summary:
            return False

        return self._calc_sha256(raw) == model.hash_mibig_summary

    @staticmethod
    def _calc_sha256(data: dict) -> str:
        json_str = json.dumps(
            data, indent=2, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return sha256(json_str.encode("utf-8")).hexdigest()

    def upsert(self, path: Path):
        with open(path) as f:
            data = json.load(f)

        model = SummaryParser().parse_mibig(data=data)
        if not model:
            return

        self.entries[path.stem] = model

    def write_to_json(self):
        payload = {
            "version_mite_data": settings.mite_version,
            "entries": {},
        }

        for _k, v in sorted(self.entries.items()):
            mibig = v.enzyme_ids.get("mibig")
            if mibig in payload["entries"]:
                payload["entries"][mibig].append(v.model_dump())
            else:
                payload["entries"][mibig] = [v.model_dump()]

        self.summary_mibig.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        self._update_metadata(payload=payload)

    def _update_metadata(self, payload: dict):
        model = ArtifactMetadata(**json.loads(self.meta_artifact.read_text()))

        model.hash_mibig_summary = self._calc_sha256(payload)
        model.version = settings.mite_version

        self.meta_artifact.write_text(model.model_dump_json(indent=2))


class SummaryGeneralStore:
    def __init__(self, data: Path, dump: Path):
        self.data = data
        self.dump = dump
        self.entries: dict[str, SummaryGeneral] = {}

        self.meta_artifact = dump / names.meta_artifact
        self.summary_json = dump / names.summary_json
        self.summary_csv = dump / names.summary_csv

    def load(self):
        """Load existing general metadata"""

        def _upsert_all():
            logger.warning(
                f"{self.summary_json}: file not found or compromised hash - re-create all entries"
            )
            for entry in self.data.glob("MITE*.json"):
                self.upsert(entry)

        if not self.summary_json.exists():
            _upsert_all()
            return

        raw = json.loads(self.summary_json.read_text())
        if self._validate_hash(raw):
            self.entries = {
                k: SummaryGeneral.model_validate(v) for k, v in raw["entries"].items()
            }
        else:
            _upsert_all()

    def _validate_hash(self, raw: dict) -> bool:
        model = ArtifactMetadata(**json.loads(self.meta_artifact.read_text()))
        if not model.hash_general_summary:
            return False

        return self._calc_sha256(raw) == model.hash_general_summary

    @staticmethod
    def _calc_sha256(data: dict) -> str:
        json_str = json.dumps(
            data, indent=2, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return sha256(json_str.encode("utf-8")).hexdigest()

    def upsert(self, path: Path):
        with open(path) as f:
            data = json.load(f)
        model = SummaryParser().parse_general(data=data)
        model = TaxonomyResolver().resolve(model)

        self.entries[path.stem] = model

    def write_to_json(self):
        payload = {
            "version_mite_data": settings.mite_version,
            "entries": {k: v.model_dump() for k, v in sorted(self.entries.items())},
        }

        self.summary_json.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        self._update_metadata(payload=payload)

    def _update_metadata(self, payload: dict):
        model = ArtifactMetadata(**json.loads(self.meta_artifact.read_text()))

        model.hash_general_summary = self._calc_sha256(payload)
        model.version = settings.mite_version

        self.meta_artifact.write_text(model.model_dump_json(indent=2))

    def write_to_csv(self):
        df = pd.DataFrame(
            [
                e.model_dump(
                    include={
                        "accession",
                        "status",
                        "enzyme_name",
                        "tailoring",
                        "cofactors_organic",
                        "cofactors_inorganic",
                        "enzyme_description",
                        "reaction_description",
                        "organism",
                        "domain",
                        "kingdom",
                        "phylum",
                        "class_name",
                        "order",
                        "family",
                    }
                )
                for e in self.entries.values()
            ]
        ).sort_values("accession")
        df.to_csv(self.summary_csv, index=False)


class SummaryService:
    """Creates summary artifact data

    Attributes:
        data: Path to data dir
        dump: Path to artifact dump dir
    """

    def __init__(self, data: Path, dump: Path):
        self.data = data
        self.dump = dump

    def create_summary_general(self, path: Path):
        """Upsert general summary"""

        logger.info(f"Started general summary creation for entry {path.name}")

        model = SummaryGeneralStore(data=self.data, dump=self.dump)
        model.load()
        model.upsert(path)
        model.write_to_json()
        model.write_to_csv()

        logger.info(f"Completed general summary creation for entry {path.name}")

    def create_summary_mibig(self, path: Path):
        """Upsert mibig summary"""

        logger.info(f"Started mibig summary creation for entry {path.name}")

        model = SummaryMibigStore(data=self.data, dump=self.dump)
        model.load()
        model.upsert(path)
        model.write_to_json()

        logger.info(f"Completed mibig summary creation for entry {path.name}")
