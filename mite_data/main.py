"""Command line interface of update functionality of mite_data

Copyright (c) 2024 to present Mitja M. Zdouc and individual contributors.

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

import logging
import sys

import coloredlogs

from mite_data.modules.fasta_manager import FastaManager
from mite_data.modules.metadata_manager import MetadataManager

logger = logging.getLogger("mite_data")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(
    coloredlogs.ColoredFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)


def main() -> SystemExit:
    """Function to execute main body of code

    Returns:
        A SystemExit code indicating the outcome of the program (0 passing, 1-n errors)
    """

    metadata_manager = MetadataManager()
    metadata_manager.run()

    fasta_manager = FastaManager()
    fasta_manager.run()

    return sys.exit(0)


if __name__ == "__main__":
    main()
