import logging
import sys

from mite_data_lib.config.config import settings
from mite_data_lib.config.logging import setup_logger
from mite_data_lib.services.mibig import MIBiGDataService

logger = logging.getLogger(__name__)


def main(service: MIBiGDataService) -> None:
    """Download MIBiG version if not existing"""
    service.check_artifacts()


if __name__ == "__main__":
    setup_logger()
    try:
        main(
            MIBiGDataService(
                version=settings.mibig_version,
                record=settings.mibig_record,
                path=settings.data / "mibig",
            )
        )
        sys.exit(0)
    except Exception as error:
        logger.fatal(f"{error!s}")
        sys.exit(1)
