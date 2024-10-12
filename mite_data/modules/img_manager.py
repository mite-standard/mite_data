"""Image (update) manager.

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

from alphafetcher import AlphaFetcher
from pydantic import BaseModel, DirectoryPath, FilePath

logger = logging.getLogger("mite_data")


class ImageManager(BaseModel):
    """Manages the download of PDB files from AlphaFold and creating of protein images.

    Attributes:
        uniprot_acc: a list of uniprot accession IDs for download
        src: a Path towards the metadata source file
        target_download: a Path towards the PDB file target (storage) directory
        target_img: a Path towards the image file target (storage) directory
    """

    uniprot_acc: list = []
    src: FilePath = Path(__file__).parent.parent.joinpath("metadata/metadata_as.json")
    target_download: DirectoryPath = Path(__file__).parent.parent.joinpath("pdb/")
    target_img: DirectoryPath = Path(__file__).parent.parent.joinpath("img/")

    def run(self: Self) -> None:
        """Class entry point to run methods"""
        logger.debug("Started ImageManager.")
        self.collect_uniprot_acc()
        self.download_pdbs()
        self.create_imgs()
        logger.debug("Completed ImageManager.")

    def collect_uniprot_acc(self: Self) -> None:
        """Collect uniprot accession IDs from the metadata file"""
        with open(self.src) as file_in:
            metadata = json.load(file_in)
        for entry in metadata["entries"]:
            if acc := metadata["entries"][entry]["enzyme_ids"].get("uniprot", None):
                self.uniprot_acc.append(acc)

    def download_pdbs(self: Self) -> None:
        """Download PDB-files from AlphaFold using the uniprot acc ids"""
        logger.debug(
            "Started download of PDB-files from AlphaFold - this will take some time."
        )

        fetcher = AlphaFetcher(base_savedir=str(self.target_download))
        fetcher.add_proteins(proteins=self.uniprot_acc)
        fetcher.download_all_files(pdb=True, multithread=True, workers=4)

        for infile in self.target_download.joinpath("pdb_files").iterdir():
            infile.rename(self.target_download / infile.name)

        self.target_download.joinpath("pdb_files").rmdir()
        logger.debug("Completed download of PDB-files from AlphaFold.")

    def create_imgs(self: Self) -> None:
        """Create PNG-images from PDB files using PyMol subprocess"""
        logger.debug(
            "Started creating images from PDB files - this will take some time."
        )

        for infile in self.target_download.iterdir():
            base_name = infile.stem
            command = [
                "pymol-oss.pymol",
                infile,
                "-d",
                f"bg_color white; hide everything; show cartoon; spectrum count, red blue; set opaque_background, 0; png img/{base_name}.png, 0, 0, -1, ray=1; quit;",
            ]
            subprocess.run(command)

        logger.debug("Completed creating images from PDB files.")
