import json
import logging
import shutil
from functools import cached_property
from hashlib import sha256
from io import StringIO
from pathlib import Path

import requests
from pydantic import ValidationError

from mite_data_lib.config.config import settings
from mite_data_lib.models.mibig import MIBiGDataAdapter, MIBiGMetadata

logger = logging.getLogger(__name__)


class MIBiGDataService:
    """Manages MIBiG reference dataset"""

    def __init__(
        self,
        version: str | None = None,
        record: str | None = None,
        path: Path | None = None,
        timeout: float | None = None,
    ):
        self.version = version or settings.mibig_version
        self.record = record or settings.mibig_record
        self.path = path or settings.data / "mibig"
        self.timeout = timeout or settings.timeout

        self.data = self.path / "mibig_proteins.json"
        self.metadata = self.path / "metadata.json"

    @cached_property
    def mibig_proteins(self) -> dict:
        """Load stored mibig protein information

        :raise:
            RuntimeError: mibig data not found
        """
        if not self._is_valid_data:
            raise RuntimeError(
                "MIBiG data does not exist, does not match expected version, or does not result in expected hash. Consider re-generating the artifact."
            )

        try:
            raw = self._load_json(self.data)
            return MIBiGDataAdapter.validate_python(raw)
        except ValidationError as e:
            raise RuntimeError(
                f"Invalid formatting of MIBIG proteins file: {self.path}"
            ) from e

    def build_artifacts(self):
        """Verify that mibig protein information exists"""
        if self._is_valid_data():
            logger.info(
                f"MIBiG data already exists in the specified version {self.version} - skip download"
            )
            return
        logger.info(
            f"MIBiG data not available, not in the expected {self.version}, or shows compromised hash - start download"
        )
        self._download_and_build()

    def _is_valid_data(self) -> bool:
        if not self._data_exists() or not self._metadata_exists():
            return False

        data = self._load_json(self.data)
        metadata = self._load_metadata()

        if metadata.version != self.version:
            return False
        if metadata.hash != self._calculate_sha256(data):
            return False

        return True

    def _data_exists(self) -> bool:
        return self.data.exists()

    def _metadata_exists(self) -> bool:
        return self.metadata.exists()

    def _load_metadata(self) -> MIBiGMetadata:
        return MIBiGMetadata(**self._load_json(self.metadata))

    @staticmethod
    def _calculate_sha256(data: dict) -> str:
        json_str = json.dumps(
            data, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return sha256(json_str.encode("utf-8")).hexdigest()

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

            data = self._download_data(metadata)
            self._write_json(path=tmp_data, data=data)

            self._write_json(
                path=tmp_metadata, data={"version": version, "record": self.record, "hash": self._calculate_sha256(data)}
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

        return {key: sorted(val) for key, val in sorted(mibig_prot.items())}

    @staticmethod
    def _write_json(path: Path, data: dict):
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False))

    @staticmethod
    def _load_json(path: Path) -> dict:
        with open(path) as f:
            return json.load(f)
