import json
import logging
import shutil
from io import StringIO
from pathlib import Path

import requests

from src.config.config import settings
from src.models.mibig import MIBiGMetadata

logger = logging.getLogger(__name__)


class MIBiGDatasetManager:
    """Manages MIBiG reference dataset"""

    def __init__(
        self,
        version: str = settings.mibig_version,
        record: str = settings.mibig_record,
        path: Path = settings.data / "mibig",
        timeout: float = settings.timeout,
    ):
        self.version = version
        self.record = record
        self.path = path
        self.timeout = timeout

        self.data = self.path / "mibig_proteins.json"
        self.metadata = self.path / "metadata.json"

    def load_data(self) -> dict:
        """Load stored mibig protein information"""
        self.ensure_data()
        return self._load_json(self.data)

    def ensure_data(self):
        """Verify that mibig protein information exists"""
        if self._is_valid_data():
            return
        self._download_and_build()

    def _is_valid_data(self) -> bool:
        if not self._data_exists() or not self._metadata_exists():
            return False

        metadata = self._load_metadata()
        if metadata.version != self.version:
            return False

        return True

    def _data_exists(self) -> bool:
        return self.data.exists()

    def _metadata_exists(self) -> bool:
        return self.metadata.exists()

    def _load_metadata(self) -> MIBiGMetadata:
        return MIBiGMetadata(**self._load_json(self.metadata))

    def _download_and_build(self):
        """Overwrites if new version is specified"""
        logger.info("Started downloading MIBiG record")

        tmp_dir = self.path.with_suffix(".tmp")

        try:
            tmp_dir.mkdir(parents=True, exist_ok=True)

            tmp_data = tmp_dir / "mibig_proteins.json"
            tmp_metadata = tmp_dir / "metadata.json"

            metadata = self._download_metadata()

            version = metadata.get("metadata", {}).get("version", {})
            if version != self.version:
                raise RuntimeError(
                    f"Mismatch between pinned version {self.version} and downloaded version {version}. Is the record link correct?"
                )

            self._write_json(path=tmp_data, data=self._download_data(metadata))

            self._write_json(
                path=tmp_metadata, data={"version": version, "record": self.record}
            )

            if self.path.exists():
                shutil.rmtree(self.path)
            tmp_dir.rename(self.path)

        finally:
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir, ignore_errors=True)

        logger.info("Completed downloading MIBiG record")

    def _download_metadata(self) -> dict:
        response_metadata = requests.get(self.record, timeout=self.timeout)
        if response_metadata.status_code != 200:
            raise RuntimeError(
                f"Error fetching 'mibig' record metadata: {response_metadata.status_code}"
            )
        return response_metadata.json()

    def _download_data(self, metadata: dict) -> dict:
        for entry in metadata.get("files"):
            if entry.get("key", "").endswith("fasta"):
                response = requests.get(entry["links"]["self"], timeout=self.timeout)
                if response.status_code != 200:
                    raise RuntimeError(
                        f"Error downloading 'mibig' record: {response.status_code}"
                    )
                fasta_text = response.content.decode("utf-8")
                return self._format(StringIO(fasta_text))

    @staticmethod
    def _format(infile: StringIO) -> dict:
        mibig_prot = {}
        for line in infile.readlines():
            if line.startswith(">"):
                accs = line.split("|")
                mibig = accs[0].removeprefix(">").split(".")[0]
                genbank = accs[-1].replace("\n", "")

                if mibig in mibig_prot:
                    mibig_prot[mibig].add(genbank)
                else:
                    mibig_prot[mibig] = set([genbank])

        return {key: list(val) for key, val in sorted(mibig_prot.items())}

    @staticmethod
    def _write_json(path: Path, data: dict):
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False))

    @staticmethod
    def _load_json(path: Path) -> dict:
        with open(path) as f:
            return json.load(f)
