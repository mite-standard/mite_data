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
import subprocess
from pathlib import Path
from typing import Self

import requests
from Bio import Entrez
from pydantic import BaseModel, DirectoryPath, FilePath

logger = logging.getLogger("mite_data")
Entrez.email = "your_email@example.com"  # must be set but does not have to be real


class BlastManager(BaseModel):
    """Manages the download of FASTA files and the building of a BLAST database.

    Not all MITE entries have NCBI GenPept accessions - some only have UniProt IDs.
    The manager first extracts accessions - MITE file does not have a GenPept ID, it will take
    the UniProt ID. Download is performed separately, but files are combined into a single BLAST DB.

    Attributes:
        genpept_acc: a list of uniprot accession IDs for download
        uniprot_acc: a list of uniprot accession IDs for download
        src: a Path towards the metadata source file
        target_download: a Path towards the fasta file target (storage) directory
        target_blast: a Path towards the blast database storage directory
    """

    genpept_acc: list = []
    uniprot_acc: list = []
    src: FilePath = Path(__file__).parent.parent.joinpath(
        "metadata/metadata_general.json"
    )
    target_download: DirectoryPath = Path(__file__).parent.parent.joinpath("fasta/")
    target_blast: DirectoryPath = Path(__file__).parent.parent.joinpath("blast_lib/")

    def run(self: Self) -> None:
        """Class entry point to run methods"""
        logger.debug("Started BlastManager.")
        self.extract_accessions()
        self.download_ncbi()
        self.download_uniprot()
        self.generate_blast_db()
        logger.debug("Completed BlastManager.")

    def extract_accessions(self: Self) -> None:
        """Extracts NCBI GenPept and UniProt accession IDs from metadata file.

        Raises:
            RuntimeError: An entry does not have a GenPept or UniProt accession ID.
        """
        with open(self.src) as file_in:
            metadata = json.load(file_in)
        for entry in metadata["entries"]:
            if acc := metadata["entries"][entry]["enzyme_ids"].get("genpept", None):
                self.genpept_acc.append((entry, acc))
            elif acc := metadata["entries"][entry]["enzyme_ids"].get("uniprot", None):
                self.uniprot_acc.append((entry, acc))
            else:
                raise RuntimeError(f"{entry} has no GenPept or UniProt ID - FIX ASAP!")

    def download_ncbi(self: Self) -> None:
        """Download protein FASTA files from NCBI GenPept"""
        if len(self.genpept_acc) == 0:
            return

        for entry in self.genpept_acc:
            handle = Entrez.efetch(
                db="protein", id=entry[1], rettype="fasta", retmode="text"
            )
            fasta_data = handle.read()
            handle.close()

            lines = fasta_data.strip().split("\n")
            if lines:
                lines[0] = f">{entry[0]}"  # Replace the header
            fasta_data = "\n".join(lines)

            with open(
                self.target_download.joinpath(f"{entry[1]}.fasta"), "w"
            ) as fasta_file:
                fasta_file.write(fasta_data)

    def download_uniprot(self: Self) -> None:
        """Download protein FASTA files from UniProt

        Raises:
            RuntimeError: Could not download UniProt data
        """

        def _store_file(entry_tuple: tuple, lines: list) -> None:
            if lines:
                lines[0] = f">{entry[0]}"
            else:
                raise RuntimeError(
                    f"UniProt download failed on ID {entry_tuple[1]} for MITE entry {entry_tuple[0]}"
                )
            payload = "\n".join(lines)
            with open(
                self.target_download.joinpath(f"{entry_tuple[1]}.fasta"), "w"
            ) as fasta_file:
                fasta_file.write(payload)

        if len(self.uniprot_acc) == 0:
            return

        for entry in self.uniprot_acc:
            logger.error(entry)
            if (
                response := requests.get(
                    f"https://rest.uniprot.org/uniprotkb/{entry[1]}.fasta"
                )
            ).status_code == 200 or (
                response := requests.get(
                    f"https://rest.uniprot.org/uniparc/{entry[1]}.fasta"
                )
            ).status_code == 200:
                _store_file(entry, response.text.strip().split("\n"))
            else:
                raise RuntimeError(
                    f"UniProt download failed on ID {entry[1]} for MITE entry {entry[0]}"
                )

    def generate_blast_db(self: Self) -> None:
        """Starts subprocess to generate a BLAST DB from the (downloaded) protein FASTA files"""
        # TODO MMZ 14.10. continue here
