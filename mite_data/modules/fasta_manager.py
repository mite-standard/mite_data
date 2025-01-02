"""Manages fasta file download and the building of a BLAST database.

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
from pathlib import Path
from typing import Self

import requests
from Bio import Entrez
from pydantic import BaseModel, DirectoryPath, FilePath

logger = logging.getLogger("mite_data")
Entrez.email = "your_email@example.com"  # must be set but does not have to be real


class FastaManager(BaseModel):
    """Manages the download of FASTA files and the building of a BLAST database.

    Not all MITE entries have NCBI GenPept accessions - some only have UniProt IDs.
    The manager first extracts accessions - MITE file does not have a GenPept ID, it will take
    the UniProtKB or UniParc ID.

    Attributes:
        genpept_acc: a list of uniprot accession IDs for download
        uniprot_acc: a list of uniprot accession IDs for download
        src: a Path towards the metadata source file
        target_download: a Path towards the fasta file target (storage) directory
    """

    genpept_acc: list = []
    uniprot_acc: list = []
    src: FilePath = Path(__file__).parent.parent.joinpath(
        "metadata/metadata_general.json"
    )
    target_download: DirectoryPath = Path(__file__).parent.parent.joinpath("fasta/")

    def run(self: Self) -> None:
        """Class entry point to run methods

        Raises:
            RuntimeError: New fasta files were downloaded (needed to abort pre-commit)

        """
        logger.info("Started FastaManager.")
        nr_files_pre = len(list(Path(self.target_download).glob("*")))
        try:
            self.extract_accessions()
            self.download_ncbi()
            self.download_uniprot()

            nr_files_post = len(list(Path(self.target_download).glob("*")))
            if nr_files_pre != nr_files_post:
                raise RuntimeError(
                    "Fasta files were downloaded - add them to version control."
                )

        except Exception as e:
            logger.error(f"An error has occurred: {e!s}")
        logger.info("Completed FastaManager.")

    def extract_accessions(self: Self) -> None:
        """Extracts NCBI GenPept and UniProt accession IDs from metadata file.

        Raises:
            RuntimeError: An entry does not have a GenPept or UniProt accession ID.
        """
        with open(self.src) as file_in:
            metadata_general = json.load(file_in)
        for entry in metadata_general["entries"]:
            if metadata_general["entries"][entry]["status"] != "active":
                logger.debug(
                    f"FastaManager: MITE entry {entry} has been retired and will not be downloaded as fasta file."
                )
                continue
            elif acc := metadata_general["entries"][entry]["enzyme_ids"].get(
                "genpept", None
            ):
                self.genpept_acc.append({"entry": entry, "acc": acc})
            elif acc := metadata_general["entries"][entry]["enzyme_ids"].get(
                "uniprot", None
            ):
                self.uniprot_acc.append({"entry": entry, "acc": acc})
            else:
                raise RuntimeError(f"{entry} has no GenPept or UniProt ID - FIX ASAP!")

    def download_ncbi(self: Self) -> None:
        """Download protein FASTA files from NCBI GenPept, skip already existing files."""
        if len(self.genpept_acc) == 0:
            logger.warning(
                f"No fasta-files scheduled to be downloaded from NCBI - SKIP"
            )
            return

        for entry in self.genpept_acc:
            if self.target_download.joinpath(f"{entry["entry"]}.fasta").exists():
                logger.debug(
                    f"File '{self.target_download.joinpath(f"{entry["entry"]}.fasta")}' already exists - SKIP"
                )
                continue

            handle = Entrez.efetch(
                db="protein", id=entry["acc"], rettype="fasta", retmode="text"
            )
            fasta_data = handle.read()
            handle.close()

            lines = fasta_data.strip().split("\n")
            if lines:
                lines[0] = f">{entry["entry"]} {entry["acc"]}"
            fasta_data = "\n".join(lines)

            with open(
                self.target_download.joinpath(f"{entry["entry"]}.fasta"), "w"
            ) as fasta_file:
                fasta_file.write(fasta_data)

    def download_uniprot(self: Self) -> None:
        """Download protein FASTA files from UniProt

        Raises:
            RuntimeError: Could not download UniProt data
        """

        def _store_file(data: dict, lines: list) -> None:
            if lines:
                lines[0] = f">{data["entry"]} {data["acc"]}"
            else:
                raise RuntimeError(
                    f"UniProt download failed on ID {data["acc"]} for MITE entry {data["entry"]}"
                )
            payload = "\n".join(lines)
            with open(
                self.target_download.joinpath(f"{data["entry"]}.fasta"), "w"
            ) as fasta_file:
                fasta_file.write(payload)

        if len(self.uniprot_acc) == 0:
            logger.warning(
                f"No fasta-files scheduled to be downloaded from UniProt - SKIP"
            )
            return

        for entry in self.uniprot_acc:
            if self.target_download.joinpath(f"{entry["entry"]}.fasta").exists():
                logger.debug(
                    f"File '{self.target_download.joinpath(f"{entry["entry"]}.fasta")}' already exists - SKIP"
                )
                continue

            if (
                response := requests.get(
                    f"https://rest.uniprot.org/uniprotkb/{entry["acc"]}.fasta"
                )
            ).status_code == 200 or (
                response := requests.get(
                    f"https://rest.uniprot.org/uniparc/{entry["acc"]}.fasta"
                )
            ).status_code == 200:
                _store_file(data=entry, lines=response.text.strip().split("\n"))
            else:
                raise RuntimeError(
                    f"UniProt download failed on ID {entry["acc"]} for MITE entry {entry["entry"]}"
                )
