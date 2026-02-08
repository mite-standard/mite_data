import json
from pathlib import Path

from mite_extras import MiteParser
from mite_schema import SchemaManager

from mite_data_lib.rules import data_rules, repo_rules

RULES_REPO = [
    "naming",
]

RULES_DATA = ["status"]


class EntryValidRunner:
    """Runs validation suite on entry"""

    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def run(self, path: Path) -> tuple[list[str], list[str]]:
        data = self._load_and_validate_schema(path)

        for rule in RULES_REPO:
            e, w = getattr(repo_rules, rule)(path)
            self.errors.extend(e)
            self.warnings.extend(w)

        for rule in RULES_DATA:
            e, w = getattr(data_rules, rule)(data)
            self.errors.extend(e)
            self.warnings.extend(w)

        return self.errors, self.warnings

    @staticmethod
    def _load_and_validate_schema(path: Path) -> dict:
        if not path.exists():
            raise FileNotFoundError(f"Could not find file {path}")

        with open(path) as f:
            data = json.load(f)

        try:
            parser = MiteParser()
            parser.parse_mite_json(data=data)
            SchemaManager().validate_mite(instance=parser.to_json())
            return data
        except Exception as e:
            raise RuntimeError(f"File {path} failed validation: {e!s}.") from e


# intended to run with CI/CD
# class to hold pipeline
# all validators i

# TODO: implement main, from __name__, main
# main
# check how many errors, warnings per file
# summarize them and pretty print
# raise os signal 1, else 0
