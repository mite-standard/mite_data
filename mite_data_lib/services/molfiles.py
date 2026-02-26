"""Create molecule info artifact files"""

import json
import logging
from hashlib import sha256
from io import StringIO
from pathlib import Path

import pandas as pd

from mite_data_lib.config.filenames import names
from mite_data_lib.models.metadata import ArtifactMetadata
from mite_data_lib.models.molfiles import MolInfo

logger = logging.getLogger(__name__)


class MolInfoParser:
    """Parses molecule information"""

    @staticmethod
    def parse(data: dict) -> [MolInfo]:
        """Parse MITE entry for mol data"""

        entries = []

        for idx_reaction, reaction in enumerate(data["reactions"], 1):
            for idx_example, example in enumerate(reaction["reactions"], 1):
                entries.append(
                    MolInfo(
                        accession=data["accession"],
                        idx_csv_smarts=f"{data['accession']}.reaction{idx_reaction}",
                        idx_csv_smiles=f"{data['accession']}.reaction{idx_reaction}.example{idx_example}",
                        reactionsmarts=reaction["reactionSMARTS"],
                        substrates=example["substrate"],
                        products=f"{'.'.join(example['products'])}",
                    )
                )

        return entries


class MolInfoStore:
    """Prepare information for molfile artifacts"""

    def __init__(self, data: Path, dump: Path):
        self.data = data
        self.dump = dump
        self.entries: list[MolInfo] = []

        self.meta_artifact = dump / names.meta_artifact
        self.smarts = dump / names.smarts
        self.smiles = dump / names.smiles

    def insert_entry(self, path: Path):
        with open(path) as f:
            data = json.load(f)

        if data["status"] != "active":
            return

        models = MolInfoParser().parse(data=data)
        self.entries.extend(models)

    def write_smarts_csv(self):
        df_smarts = (
            pd.DataFrame(
                [
                    e.model_dump(include={"idx_csv_smarts", "reactionsmarts"})
                    for e in self.entries
                ]
            )
            .rename(columns={"idx_csv_smarts": "mite_id"})
            .sort_values("mite_id")
        )
        df_smarts.to_csv(self.smarts, index=True)
        self._update_metadata(ref="smarts", hash_val=self._calc_sha256_csv(df_smarts))

    def write_smiles_csv(self):
        df_smiles = (
            pd.DataFrame(
                [
                    e.model_dump(
                        include={
                            "idx_csv_smiles",
                            "substrates",
                            "products",
                        }
                    )
                    for e in self.entries
                ]
            )
            .rename(columns={"idx_csv_smiles": "mite_id"})
            .sort_values("mite_id")
        )
        df_smiles.to_csv(self.smiles, index=True)
        self._update_metadata(ref="smiles", hash_val=self._calc_sha256_csv(df_smiles))

    def _update_metadata(self, ref: str, hash_val: str):
        model = ArtifactMetadata(**json.loads(self.meta_artifact.read_text()))
        setattr(model, ref, hash_val)
        self.meta_artifact.write_text(model.model_dump_json(indent=2))

    @staticmethod
    def _calc_sha256_csv(df: pd.DataFrame) -> str:
        buffer = StringIO()
        df.to_csv(buffer, index=True, lineterminator="\n")
        return sha256(buffer.getvalue().encode("utf-8")).hexdigest()


class MolInfoService:
    """Creates molfile artifact data

    Attributes:
        data: Path to data dir
        dump: Path to artifact dump dir
    """

    def __init__(self, data: Path, dump: Path):
        self.data = data
        self.dump = dump

    def create_molfiles(self):
        logger.info(f"Started molfile artifact creation")

        model = MolInfoStore(data=self.data, dump=self.dump)

        for entry in sorted(self.data.glob("MITE*.json")):
            model.insert_entry(entry)
        model.write_smarts_csv()
        model.write_smiles_csv()

        logger.info(f"Completed molfile artifact creation")
