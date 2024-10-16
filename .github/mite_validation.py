"""MITE validation CI/CD pipeline, to be used with pre-commit.

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
from pathlib import Path
from typing import Self

from pydantic import BaseModel, DirectoryPath


class MetadataManager(BaseModel):
    """Manage methods to validate MITE entries in pre-commit and CI/CD

    Attributes:
        src: a Path towards the source directory
    """

    src: DirectoryPath = Path(__file__).parent.parent.joinpath("mite_data/data/")

    def run(self: Self) -> None:
        """Function to run all validation steps"""
        self.check_duplicates()
        # TODO MMZ 15.10: implement self.validate_entries_passing()

    def check_duplicates(self: Self) -> None:
        """Check if multiple MITE entries describe the same enzyme using GenPept/UniProt IDs

        Raises:
            RuntimeError: Duplicate entry detected OR entry without uniprot or ncbi ID detected
        """
        nr_ncbi = {}
        nr_uniprot = {}

        for entry in self.src.iterdir():
            with open(entry) as infile:
                mite_json = json.load(infile)

            if mite_json["status"] != "active":
                continue
            elif acc := mite_json["enzyme"]["databaseIds"].get("genpept", None):
                if acc in nr_ncbi:
                    raise RuntimeError(
                        f"Duplicate entry {entry.name}: {acc} already found in entry {nr_ncbi[acc]}."
                    )
                else:
                    nr_ncbi[acc] = entry.name
            elif acc := mite_json["enzyme"]["databaseIds"].get("uniprot", None):
                if acc in nr_uniprot:
                    raise RuntimeError(
                        f"Duplicate entry {entry.name}: {acc} already found in entry {nr_uniprot[acc]}."
                    )
                else:
                    nr_uniprot[acc] = entry.name
            else:
                raise RuntimeError(
                    f"Entry {entry.name} has neither an UniProt nor an NCBI GenPept accession."
                )

    def validate_entries_passing(self: Self) -> None:
        """Check if MITE entries pass automated validation checks of mite_extras

        Raises:
            Exception: MITE entry did not pass the automated validation
        """
        # TODO MMZ 15.10: implement after mite_extras is available via PyPI


if __name__ == "__main__":
    manager = MetadataManager()
    manager.run()
