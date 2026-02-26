import json
from pathlib import Path

import pytest

from mite_data_lib.models.summary import SummaryGeneral, SummaryMibig
from mite_data_lib.services.summary import SummaryParser, TaxonomyResolver

path = Path("tests/dummy_data/data/MITE0000000.json")


def test_summary_parser_general():
    with open(path, "r") as f:
        data = json.load(f)
    model = SummaryParser().parse_general(data)
    assert isinstance(model, SummaryGeneral)


def test_summary_parser_mibig():
    with open(path, "r") as f:
        data = json.load(f)
    model = SummaryParser().parse_mibig(data)
    assert isinstance(model, SummaryMibig)


@pytest.mark.download
def test_resolve_uniprot():
    with open(path, "r") as f:
        data = json.load(f)
    model = SummaryParser().parse_general(data)
    model = TaxonomyResolver().resolve(model)
    assert model.organism == "Streptomyces viridochromogenes Tue57"


@pytest.mark.download
def test_resolve_ncbi():
    with open(path, "r") as f:
        data = json.load(f)
    model = SummaryParser().parse_general(data)
    model.enzyme_ids = {"genpept": "AAK83184.1"}
    model = TaxonomyResolver().resolve(model)
    assert model.organism == "Streptomyces viridochromogenes Tue57"
