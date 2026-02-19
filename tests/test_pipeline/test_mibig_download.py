from pathlib import Path

from mite_data_lib.services.mibig import MIBiGDataService
from pipeline.mibig_download import main


def test_mibig_main_valid():
    assert (
        main(
            MIBiGDataService(
                version="4.0.1",
                record="https://zenodo.org/api/records/13367755",
                path=Path("tests/dummy_data/mibig_valid"),
                timeout=10,
            )
        )
        is None
    )
