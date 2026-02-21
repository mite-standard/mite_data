import logging

from mite_data_lib.config.config import settings
from mite_data_lib.config.logging import setup_logger
from mite_data_lib.services.mibig import MIBiGDataService

logger = logging.getLogger(__name__)


def main(service: MIBiGDataService) -> None:
    """Download MIBiG version if not existing"""
    logger.info("Started with MIBiG dataset download")
    logger.info(
        f"MIBiG version {settings.mibig_version} specified in mite_data_lib/config/config.py"
    )
    service.build_artifacts()


if __name__ == "__main__":
    setup_logger()
    main(MIBiGDataService())
