"""Command line interface manager.

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

import argparse
from importlib import metadata

from pydantic import BaseModel


class CliManager(BaseModel):
    """Manage command line interface and parsing."""

    @staticmethod
    def run(args: list) -> argparse.Namespace:
        """Run command line interface using argparse.

        Arguments:
            args: specified arguments

        Returns:
            argparse.Namespace object with command line parameters
        """
        parser = argparse.ArgumentParser(
            description=f"'mite_data' CLI v{metadata.version('mite_data')}.",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        parser.add_argument(
            "--update_md",
            action="store_true",
            default=False,
            help="Updates the metadata-cache.",
        )

        parser.add_argument(
            "--update_img",
            action="store_true",
            default=False,
            help="Updates the AlphaFold-derived PDB-files and re-generates protein images with PyMol.",
        )

        parser.add_argument(
            "--update_blast",
            action="store_true",
            default=False,
            help="Updates the Genbank-derived protein FASTA-files and re-generates the BLAST database.",
        )

        parser.add_argument(
            "--update_mite",
            action="store_true",
            default=False,
            help="Runs automated checks on MITE entries and updates to latest schema version using 'mite_extras'.",
        )

        parser.add_argument(
            "--update_all",
            action="store_true",
            default=False,
            help="Runs all update actions at once.",
        )

        parser.add_argument(
            "-v",
            "--verboseness",
            type=str,
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            required=False,
            help="Specifies the verboseness of logging (default: 'INFO').",
        )

        return parser.parse_args(args)
