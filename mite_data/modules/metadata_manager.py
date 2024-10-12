"""Metadata (update) manager.

Copyright (c) 2024 to present Mitja Maximilian Zdouc, PhD and individual contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import logging
from datetime import datetime
from importlib import metadata
from pathlib import Path
from typing import Self

from pydantic import BaseModel, DirectoryPath

logger = logging.getLogger("mite_data")


class MetadataManager(BaseModel):
    """Manage metadata collection from MITE entries.

    Attributes:
        metadata_as: a dict collecting MITE metadata with MITE IDs as keys
        metadata_mibig: a dict collecting MITE metadata with MIBiG IDs as keys
    """

    src: DirectoryPath = Path(__file__).parent.parent.joinpath("data/")
    target: DirectoryPath = Path(__file__).parent.parent.joinpath("metadata/")
    metadata_as: dict = {
        "created": f"{datetime.now()}",
        "version_mite_data": f"{metadata.version('mite_data')}",
        "entries": {},
    }
    metadata_mibig: dict = {
        "created": f"{datetime.now()}",
        "version_mite_data": f"{metadata.version('mite_data')}",
        "entries": {},
    }

    def run(self: Self) -> None:
        """Class entry point to run methods"""
        logger.debug("Started update metadata.")
        self.collect_metadata()
        self.export_json()
        logger.debug("Completed update metadata.")

    def collect_metadata(self: Self) -> None:
        """Method to access and collect metadata from MITE entries"""
        for infile in self.src.iterdir():
            with open(infile) as file_in:
                mite_json = json.load(file_in)
            self.extract_metadata_as(mite=mite_json)
            self.extract_metadata_mibig(mite=mite_json)

    def extract_metadata_as(self: Self, mite: dict) -> None:
        """Extract and stores metadata with MITE IDs as keys

        mite: the MITE JSON derived dict to extract data from
        """
        self.metadata_as["entries"][mite["accession"]] = {
            "status": mite["status"],
            "mite_url": f"https://mite.bioinformatics.nl/repository/{mite["accession"]}",
            "enzyme_name": mite["enzyme"]["name"],
            "enzyme_description": mite.get("enzyme", {}).get(
                "description", "No description available"
            ),
            "enzyme_ids": mite["enzyme"]["databaseIds"],
            "enzyme_tailoring": "|".join(
                list(
                    {
                        tailoring
                        for reaction in mite.get("reactions")
                        for tailoring in reaction.get("tailoring", [])
                    }
                )
            ),
        }

    def extract_metadata_mibig(self: Self, mite: dict) -> None:
        """Extract and stores metadata with MIBiG IDs as keys

        mite: the MITE JSON derived dict to extract data from
        """
        self.metadata_mibig["entries"][
            mite.get("enzyme", {}).get("databaseIds", {}).get("mibig", "BGC0000000")
        ] = {
            "mite_accession": mite.get("accession"),
            "mite_url": f"https://mite.bioinformatics.nl/repository/{mite["accession"]}",
            "status": mite["status"],
            "enzyme_name": mite["enzyme"]["name"],
            "enzyme_description": mite.get("enzyme", {}).get(
                "description", "No description available"
            ),
            "enzyme_ids": mite["enzyme"]["databaseIds"],
            "enzyme_tailoring": "|".join(
                list(
                    {
                        tailoring
                        for reaction in mite.get("reactions")
                        for tailoring in reaction.get("tailoring", [])
                    }
                )
            ),
            "enzyme_refs": mite["enzyme"]["references"],
        }

    def export_json(self: Self) -> None:
        """Exports collected metadata dicts to target dir"""
        with open(
            self.target.joinpath("metadata_as.json"), "w", encoding="utf-8"
        ) as outfile:
            outfile.write(json.dumps(self.metadata_as, indent=2, ensure_ascii=False))

        with open(
            self.target.joinpath("metadata_mibig.json"), "w", encoding="utf-8"
        ) as outfile:
            outfile.write(json.dumps(self.metadata_mibig, indent=2, ensure_ascii=False))
