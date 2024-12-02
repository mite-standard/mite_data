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
from importlib import metadata
from pathlib import Path
from typing import Self

from pydantic import BaseModel, DirectoryPath

logger = logging.getLogger("mite_data")


class MetadataManager(BaseModel):
    """Manage metadata collection from MITE entries.

    Attributes:
        src: a Path towards the source directory
        target: a Path towards the target (storage) directory
        metadata_general: a dict collecting MITE metadata with MITE IDs as keys for internal use
        metadata_mibig: a dict collecting MITE metadata
        metadata_efi_est: a list collecting metadata for efi-est
        fasta_efi_est: a list collecting fasta data for efi-est
    """

    src: DirectoryPath = Path(__file__).parent.parent.joinpath("data/")
    target: DirectoryPath = Path(__file__).parent.parent.joinpath("metadata/")
    metadata_general: dict = {
        "version_mite_data": f"{metadata.version('mite_data')}",
        "entries": {},
    }
    metadata_mibig: dict = {
        "version_mite_data": f"{metadata.version('mite_data')}",
        "entries": {},
    }
    metadata_efi_est: list = [
        "key,mite_acc,enzyme_name,enzyme_description,tailoring,id_uniprot,id_genpept,id_mibig\n"
    ]
    fasta_efi_est: list = []

    def run(self: Self) -> None:
        """Class entry point to run methods"""
        logger.debug("Started MetadataManager.")
        self.collect_metadata()
        self.export_json()
        self.efi_est_files()
        logger.debug("Completed MetadataManager.")

    def collect_metadata(self: Self) -> None:
        """Method to access and collect metadata from MITE entries"""
        for infile in self.src.iterdir():
            with open(infile) as file_in:
                mite_json = json.load(file_in)
            self.extract_metadata_general(mite=mite_json)
            self.extract_metadata_mibig(mite=mite_json)

    def extract_metadata_general(self: Self, mite: dict) -> None:
        """Extract and stores metadata with MITE IDs as keys

        mite: the MITE JSON derived dict to extract data from
        """
        self.metadata_general["entries"][mite["accession"]] = {
            "status": mite["status"],
            "enzyme_name": mite["enzyme"]["name"],
            "enzyme_description": mite.get("enzyme", {}).get(
                "description", "No description available"
            ),
            "enzyme_ids": mite["enzyme"]["databaseIds"],
        }

    def extract_metadata_mibig(self: Self, mite: dict) -> None:
        """Extract and stores metadata with MIBiG IDs as keys

        mite: the MITE JSON derived dict to extract data from
        """
        mibig = mite.get("enzyme", {}).get("databaseIds", {}).get("mibig")
        if mibig is None:
            return

        entry = {
            "mite_accession": mite["accession"],
            "mite_url": f"https://mite.bioinformatics.nl/repository/{mite["accession"]}",
            "status": mite["status"],
            "enzyme_name": mite["enzyme"]["name"],
            "enzyme_description": mite["enzyme"].get(
                "description", "No description available"
            ),
            "enzyme_ids": mite["enzyme"]["databaseIds"],
            "enzyme_tailoring": "|".join(
                sorted(
                    {
                        tailoring
                        for reaction in mite.get("reactions")
                        for tailoring in reaction.get("tailoring", [])
                    }
                )
            ),
            "enzyme_refs": mite["enzyme"]["references"],
        }

        if mibig in self.metadata_mibig["entries"]:
            self.metadata_mibig["entries"][mibig].append(entry)
        else:
            self.metadata_mibig["entries"][mibig] = [entry]

    def efi_est_files(self: Self) -> None:
        """Collects data for EFI-EST sequence similarity network"""
        fasta_dir = Path(__file__).parent.parent.joinpath("fasta")

        index = 0
        for fasta_file in fasta_dir.iterdir():
            with open(fasta_file) as infile:
                lines = infile.read()
                split_lines = lines.splitlines()
                mite_acc = split_lines[0].split("|")[0].strip(">")

            with open(self.src.joinpath(f"{mite_acc}.json")) as mite_file:
                mite_data = json.load(mite_file)

            key = f"{index}".rjust(7, "z")
            acc = mite_data["accession"]
            name = mite_data["enzyme"].get("name", "").replace(",", "")
            descr = mite_data["enzyme"].get("description", "").replace(",", "")
            tail = "|".join(
                sorted(
                    {
                        tailoring
                        for reaction in mite_data.get("reactions")
                        for tailoring in reaction.get("tailoring", [])
                    }
                )
            )
            uniprot = mite_data["enzyme"]["databaseIds"].get("uniprot", "")
            genpept = mite_data["enzyme"]["databaseIds"].get("genpept", "")
            mibig = mite_data["enzyme"]["databaseIds"].get("mibig", "")

            self.metadata_efi_est.append(
                f"{key},{acc},{name},{descr},{tail},{uniprot},{genpept},{mibig}\n"
            )

            self.fasta_efi_est.append(f"{lines}\n")

            index += 1

        with open(
            self.target.joinpath("metadata_efi_est.csv"), "w", encoding="utf-8"
        ) as outfile:
            outfile.writelines(self.metadata_efi_est)

        with open(
            self.target.joinpath("efi_est.fasta"), "w", encoding="utf-8"
        ) as outfile:
            outfile.writelines(self.fasta_efi_est)

        # dump data here

    def export_json(self: Self) -> None:
        """Exports collected metadata to target dir"""
        with open(
            self.target.joinpath("metadata_general.json"), "w", encoding="utf-8"
        ) as outfile:
            outfile.write(
                json.dumps(self.metadata_general, indent=2, ensure_ascii=False)
            )

        with open(
            self.target.joinpath("metadata_mibig.json"), "w", encoding="utf-8"
        ) as outfile:
            outfile.write(json.dumps(self.metadata_mibig, indent=2, ensure_ascii=False))
