from mite_data.modules.metadata_manager import MetadataManager


def test_init_valid():
    assert isinstance(MetadataManager(), MetadataManager)
