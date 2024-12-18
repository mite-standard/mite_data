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
from sys import argv
from typing import Self

from mite_extras import MiteParser
from mite_schema import SchemaManager
from pydantic import BaseModel, DirectoryPath, model_validator


class CicdManager(BaseModel):
    """Manage methods to validate MITE entries in pre-commit and CI/CD

    Attributes:
        src: a Path towards the source directory
        issues: all issues detected during run
        genpept: a list of genbank accessions in mite_data
        uniprot: a list of uniprot accessions in mite_data
    """

    src: DirectoryPath = Path(__file__).parent.parent.joinpath("mite_data/data/")
    issues: list = []
    genpept: dict = {}
    uniprot: dict = {}

    @model_validator(mode="after")
    def fill_accessions(self):
        for entry in self.src.iterdir():
            with open(entry) as infile:
                data = json.load(infile)
            if data["status"] != "active":
                continue

            if acc := data["enzyme"]["databaseIds"].get("genpept", None):
                if acc in self.genpept:
                    self.genpept[acc].append(data["accession"])
                else:
                    self.genpept[acc] = [data["accession"]]

            if acc := data["enzyme"]["databaseIds"].get("uniprot", None):
                if acc in self.uniprot:
                    self.uniprot[acc].append(data["accession"])
                else:
                    self.uniprot[acc] = [data["accession"]]

        return self

    def run_file(self: Self, path: str) -> None:
        """Run a single file against validation functions

        Arguments:
            path: a file path

        Raises:
            FileNotFoundError: file not found
            RuntimeError: one or more issues with files detected
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Could not find file '{path}'")

        if not path.name.startswith("MITE"):
            raise RuntimeError(f"File '{path.name}' does not appear to be a MITE file.")

        with open(path) as infile:
            data = json.load(infile)

        self.check_release_ready(data=data)
        self.check_duplicates(data=data)
        self.validate_entries_passing(data=data)

        if len(self.issues) != 0:
            raise RuntimeError("\n".join(self.issues))

    def run_data_dir(self: Self) -> None:
        """Run all files against validation functions

        Raises:
            FileNotFoundError: file not found
            RuntimeError: one or more issues with files detected
        """
        for path in self.src.iterdir():
            if not path.exists():
                raise FileNotFoundError(f"Could not find file '{path}'")

            if not path.name.startswith("MITE"):
                raise RuntimeError(
                    f"File '{path.name}' does not appear to be a MITE file."
                )

            with open(path) as infile:
                data = json.load(infile)
            if data["status"] != "active":
                continue

            self.check_release_ready(data=data)
            self.check_duplicates(data=data)
            self.validate_entries_passing(data=data)

        if len(self.issues) != 0:
            raise RuntimeError("\n".join(self.issues))

    def check_release_ready(self: Self, data: dict) -> None:
        """Verify that entry does not have the status tag 'pending' or the MITE ID MITE9999999

        Argument:
            data: the mite entry data
        """
        if data["status"] == "pending":
            self.issues.append(
                f"Entry '{data["accession"]}' has the status flag 'pending'. This must be set to 'active' before release."
            )

        if data["accession"] == "MITE9999999":
            self.issues.append(
                f"Entry '{data["accession"]}' has the MITE accession 'MITE9999999'. Change this to the correct accession before release."
            )

    def check_duplicates(self: Self, data: dict) -> None:
        """Check if multiple MITE entries describe the same enzyme using GenPept/UniProt IDs

        Argument:
            data: the mite entry data
        """
        if data["status"] != "active":
            return

        if acc := data["enzyme"]["databaseIds"].get("genpept", None):
            if len(self.genpept[acc]) > 1:
                self.issues.append(
                    f"Multiple entries share the same GenPept ID '{acc}': '{self.genpept[acc]}'"
                )

        if acc := data["enzyme"]["databaseIds"].get("uniprot", None):
            if len(self.uniprot[acc]) > 1:
                self.issues.append(
                    f"Multiple entries share the same UniProt ID '{acc}': '{self.uniprot[acc]}'"
                )

    def validate_entries_passing(self: Self, data: dict) -> None:
        """Check if MITE entries pass automated validation checks of mite_extras

        Argument:
            data: the mite entry data
        """
        try:
            parser = MiteParser()
            parser.parse_mite_json(data=data)
            schema_manager = SchemaManager()
            schema_manager.validate_mite(instance=parser.to_json())
        except Exception as e:
            self.issues.append(
                f"Error: entry {data["accession"]} failed validation ({e})."
            )


if __name__ == "__main__":
    manager = CicdManager()

    try:
        manager.run_file(path=argv[1])
    except IndexError:
        manager.run_data_dir()
