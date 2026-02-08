import re
from importlib import metadata
from pathlib import Path

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Centralized config"""

    data: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent.joinpath(
            "mite_data"
        )
    )

    @property
    def mibig_version(self) -> str:
        return "4.0.1"

    @property
    def mibig_record(self) -> str:
        return "https://zenodo.org/api/records/13367755"  # version 4.0.1

    @property
    def timeout(self) -> float:
        return 10

    @property
    def mite_version(self) -> str:
        return metadata.version("mite_data")

    @property
    def mite_pattern(self) -> re.Pattern:
        return re.compile(r"^MITE(\d{7})$")


settings = Settings()
