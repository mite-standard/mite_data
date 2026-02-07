import json
import logging
import os
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

    def update_from_entry(self, path: Path):
        """Update data for a single entry"""
        self._ensure_prot_acc()

        df = self._load_prot_acc()

        metadata = self._load_metadata()

        if metadata.version != settings.mite_version:
            logger.warning(f"MITE version update detected: rebuilding files")
            self._build()
            return

        if metadata.hash_mite_prot_acc != self._calculate_sha256(df):
            logger.warning(
                f"Hash-based integrity of {self.prot_acc.name} compromised: rebuilding files"
            )
            self._build()
            return

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
        df = pd.concat([df, df_entry])
        df = df[~df.index.duplicated(keep="last")]
        df.sort_index(inplace=True)
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
        for entry in sorted(self.data.glob("*.json")):
            data = self._parse_entry(entry)
            df_dict["accession"].append(data["accession"])
            df_dict["status"].append(data["status"])
            df_dict["genpept"].append(data["genpept"])
            df_dict["uniprot"].append(data["uniprot"])

        df = pd.DataFrame(df_dict)
        df.set_index("accession", inplace=True)
        df.sort_index(inplace=True)

        try:
            metadata = self._load_metadata()
            metadata.hash_mite_prot_acc = self._calculate_sha256(df)
            metadata.version = settings.mite_version
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
        return pd.read_csv(self.prot_acc, index_col="accession")

    def _write_prot_acc(self, df: pd.DataFrame):
        tmp = self.prot_acc.with_suffix(".tmp")
        df.to_csv(tmp, index=True, lineterminator="\n")
        tmp.replace(self.prot_acc)

    def _load_metadata(self) -> ArtifactMetadata:
        return ArtifactMetadata(**self._load_json(self.metadata))

    def _write_metadata(self, data: ArtifactMetadata):
        tmp = self.metadata.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(data.model_dump_json())
        tmp.replace(self.metadata)

    @staticmethod
    def _load_json(path: Path) -> dict:
        with open(path) as f:
            return json.load(f)
