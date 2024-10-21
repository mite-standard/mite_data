"""MITE entries (update) manager.

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

from mite_extras import MiteParser
from mite_schema import SchemaManager
from pydantic import BaseModel, DirectoryPath

logger = logging.getLogger("mite_data")


class MiteManager(BaseModel):
    """Manage updating/validating the MITE entries.

    Attributes:
        src: a Path to the data source directory
    """

    src: DirectoryPath = Path(__file__).parent.parent.joinpath("data/")

    def run(self: Self) -> None:
        """Method to validate/update MITE entries. Overwrites all old entries"""
        logger.debug("Started MiteManager.")

        schema_manager = SchemaManager()

        for entry in self.src.iterdir():
            try:
                if not entry.name.startswith("MITE") or not entry.name.endswith(
                    ".json"
                ):
                    continue

                logger.debug(f"MiteManager: started processing of file '{entry.name}'.")

                with open(entry) as infile:
                    input_data = json.load(infile)

                parser = MiteParser()
                parser.parse_mite_json(data=input_data)

                schema_manager.validate_mite(instance=parser.to_json())

                with open(file=entry, mode="w", encoding="utf-8") as outfile:
                    outfile.write(
                        json.dumps(parser.to_json(), indent=4, ensure_ascii=False)
                    )

                logger.debug(
                    f"MiteManager: completed processing of file '{entry.name}'."
                )
            except Exception as e:
                logger.fatal(f"MiteManager: entry {entry.name} failed validation")
                raise e

        logger.debug("Completed MiteManager")
