import json
import logging
from hashlib import sha256
from io import StringIO
from pathlib import Path

import pandas as pd

from mite_data_lib.config.config import settings
from mite_data_lib.models.metadata import ArtifactMetadata

logger = logging.getLogger(__name__)


class DeriveProtAccessions:
    """Manages mite accession file artifact generation"""

    def __init__(
        self,
        data: Path = settings.data / "data",
        dump: Path = settings.data / "metadata",
    ):
        self.data = data
        self.dump = dump

        self.prot_acc = self.dump / "mite_prot_accessions.csv"
        self.metadata = self.dump / "artifact_metadata.json"

    def update_prot_acc(self, path: Path):
        """Update data for a single entry"""
        self._ensure_prot_acc()

        df = self._load_prot_acc()
        df.set_index("accession", inplace=True)

        metadata = self._load_metadata()
        if metadata.hash_mite_prot_acc != self._calculate_sha256(df):
            raise ValueError(
                f"Hash-based integrity of {self.prot_acc.name} compromised"
            )

        if not path.exists():
            raise FileNotFoundError(f"Did not find {path.name}")

        entry = self._parse_entry(path)
        df_entry = pd.DataFrame(
            {
                "accession": [entry["accession"]],
                "status": [entry["status"]],
                "genpept": [entry["genpept"]],
                "uniprot": [entry["uniprot"]],
            }
        )
        df_entry.set_index("accession", inplace=True)

        df.update(df_entry)
        metadata.hash_mite_prot_acc = self._calculate_sha256(df)

        self._write_prot_acc(df)
        self._write_metadata(metadata)

    def create_prot_acc(self):
        """Create derived file and dump to disk"""
        self._build()

    def _ensure_prot_acc(self):
        if self._prot_acc_exists() and self._metadata_exists():
            return
        self._build()

    def _prot_acc_exists(self):
        return self.prot_acc.exists()

    def _metadata_exists(self) -> bool:
        return self.metadata.exists()

    def _build(self):
        df_dict = {"accession": [], "status": [], "genpept": [], "uniprot": []}
        for entry in self.data.iterdir():
            data = self._parse_entry(entry)
            df_dict["accession"].append(data["accession"])
            df_dict["status"].append(data["status"])
            df_dict["genpept"].append(data["genpept"])
            df_dict["uniprot"].append(data["uniprot"])

        df = pd.DataFrame(df_dict)
        df.sort_values(by=["accession"], ascending=True, inplace=True)
        df.set_index("accession", inplace=True)

        try:
            metadata = self._load_metadata()
            metadata.hash_mite_prot_acc = self._calculate_sha256(df)
        except FileNotFoundError:
            logger.warning("Could not find artifact metadata - build from scratch")
            metadata = ArtifactMetadata(
                version=settings.mite_version,
                hash_mite_prot_acc=self._calculate_sha256(df),
            )

        self._write_prot_acc(df)
        self._write_metadata(metadata)

    def _parse_entry(self, path: Path) -> dict:
        data = self._load_json(path)
        return {
            "accession": data["accession"],
            "status": data["status"],
            "genpept": data["enzyme"]["databaseIds"].get("genpept"),
            "uniprot": data["enzyme"]["databaseIds"].get("uniprot"),
        }

    @staticmethod
    def _calculate_sha256(df: pd.DataFrame) -> str:
        buffer = StringIO()
        df.to_csv(buffer, index=True, lineterminator="\n")
        return sha256(buffer.getvalue().encode("utf-8")).hexdigest()

    def _load_prot_acc(self) -> pd.DataFrame:
        return pd.read_csv(self.prot_acc)

    def _write_prot_acc(self, df: pd.DataFrame):
        df.to_csv(self.prot_acc, index=True, lineterminator="\n")

    def _load_metadata(self) -> ArtifactMetadata:
        return ArtifactMetadata(**self._load_json(self.metadata))

    def _write_metadata(self, data: ArtifactMetadata):
        with open(self.metadata, "w", encoding="utf-8") as f:
            f.write(data.model_dump_json())

    @staticmethod
    def _load_json(path: Path) -> dict:
        with open(path) as f:
            return json.load(f)
