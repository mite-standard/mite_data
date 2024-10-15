"""Command line interface of mite_data

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
from importlib import metadata

import coloredlogs

from mite_data.modules.blast_manager import BlastManager
from mite_data.modules.cli_manager import CliManager
from mite_data.modules.img_manager import ImageManager
from mite_data.modules.metadata_manager import MetadataManager


def config_logger(verboseness: str) -> logging.Logger:
    """Set up a named logger with nice formatting

    Args:
        verboseness: sets the logging verboseness

    Returns:
        A Logger object
    """
    root_logger = logging.getLogger()
    root_logger.removeHandler(root_logger.handlers[0])

    logger = logging.getLogger("mite_data")
    logger.setLevel(getattr(logging, verboseness))
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        coloredlogs.ColoredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    )
    logger.addHandler(console_handler)
    return logger


def main() -> SystemExit:
    """Function to execute main body of code

    Returns:
        A SystemExit code indicating the outcome of the program (0 passing, 1-n errors)
    """

    args = CliManager().run(sys.argv[1:])
    logger = config_logger(args.verboseness)

    logger.debug(f"Started 'mite_data' v{metadata.version('mite_data')} as CLI.")

    metadata_manager = MetadataManager()
    metadata_manager.run()

    if args.update_img or args.update_all:
        img_manager = ImageManager()
        img_manager.run()

    if args.update_blast or args.update_all:
        blast_manager = BlastManager()
        blast_manager.run()

    if args.update_mite or args.update_all:
        logger.debug("Started update MITE entries.")
        # TODO MMZ 12.10: implement after mite_extras is available via PyPI
        logger.debug("Completed update MITE entries.")

    logger.debug(f"Completed 'mite_data' v{metadata.version('mite_data')} as CLI.")

    return sys.exit(0)


if __name__ == "__main__":
    main()
