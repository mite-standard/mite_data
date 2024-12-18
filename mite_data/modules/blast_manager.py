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
import os
import shutil
import subprocess
from importlib import metadata
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
    the UniProtKB or UniParc ID.
    Download is performed separately, but files are combined into a single BLAST DB.

    Attributes:
        genpept_acc: a list of uniprot accession IDs for download
        uniprot_acc: a list of uniprot accession IDs for download
        src: a Path towards the metadata source file
        target_download: a Path towards the fasta file target (storage) directory
        target_blast: a Path towards the blast database storage directory
        concat_filename: filename of the concatenated fasta file
    """

    genpept_acc: list = []
    uniprot_acc: list = []
    src: FilePath = Path(__file__).parent.parent.joinpath(
        "metadata/metadata_general.json"
    )
    target_download: DirectoryPath = Path(__file__).parent.parent.joinpath("fasta/")
    target_blast: DirectoryPath = Path(__file__).parent.parent.joinpath("blast_lib/")
    concat_filename: str = "mite_enzymes_concat.fasta"

    def run(self: Self) -> None:
        """Class entry point to run methods"""
        logger.debug("Started BlastManager.")
        try:
            self.extract_accessions()
            self.download_ncbi()
            self.download_uniprot()
            self.concat_fasta_files()
            self.validate_nr_files()
            self.generate_blast_db()
        except Exception as e:
            logger.error(f"An error has occurred: {e!s}")
        logger.debug("Completed BlastManager.")

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
                    f"BlastManager: MITE entry {entry} has been retired and will not be included in the BLAST DB."
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
                logger.info(
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
                logger.info(
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

    def validate_nr_files(self: Self) -> None:
        """Validate that number of downloaded files equals to number of active entries

        Raises:
            RuntimeError: Not all files were downloaded
        """
        with open(self.src) as file_in:
            metadata_general = json.load(file_in)

        expected_set = set()
        for entry in metadata_general["entries"]:
            if metadata_general["entries"][entry]["status"] == "active":
                if genpept := metadata_general["entries"][entry]["enzyme_ids"].get(
                    "genpept", None
                ):
                    expected_set.add(f"{genpept}.fasta")
                else:
                    expected_set.add(
                        f"{metadata_general["entries"][entry]["enzyme_ids"].get("uniprot")}.fasta"
                    )

        expected_set = set()
        for key in metadata_general["entries"]:
            if metadata_general["entries"][key]["status"] == "active":
                expected_set.add(key)

        present_set = set()
        for f in self.target_download.iterdir():
            if f.suffix == ".fasta":
                present_set.add(f)

        if len(expected_set) != len(present_set):
            raise RuntimeError(
                f"BlastManager: Not all expected FASTA files were downloaded. "
                f"Expected files were: {expected_set}."
                f"Missing files are: {expected_set.difference(present_set)}."
            )

    def concat_fasta_files(self: Self) -> None:
        """Concatenates individual FASTA files into a single one."""
        with open(self.target_blast.joinpath(self.concat_filename), "w") as outfile:
            for filename in self.target_download.iterdir():
                if filename.suffix == ".fasta" and filename != self.concat_filename:
                    with open(filename) as infile:
                        shutil.copyfileobj(infile, outfile)
                        outfile.write("\n")

    def generate_blast_db(self: Self) -> None:
        """Starts subprocess to generate a BLAST DB from the (downloaded) protein FASTA files"""
        logger.debug("Started creating BLAST DB.")

        temp_dir = self.target_blast.joinpath("temp_dir")
        temp_dir.mkdir(parents=True, exist_ok=True)

        command = [
            "makeblastdb",
            "-in",
            f"{self.target_blast.joinpath(self.concat_filename)}",
            "-dbtype",
            "prot",
            "-out",
            f"{temp_dir.joinpath("mite_blastfiles")}",
            "-title",
            f"MITE v{metadata.version('mite_data')} BLAST DB",
        ]
        subprocess.run(command, check=True)
        os.remove(self.target_blast.joinpath(self.concat_filename))

        shutil.make_archive(
            base_name=str(self.target_blast.joinpath("MiteBlastDB")),
            format="zip",
            root_dir=temp_dir,
            base_dir=".",
        )
        shutil.rmtree(temp_dir)

        logger.debug("Completed creating BLAST DB.")
