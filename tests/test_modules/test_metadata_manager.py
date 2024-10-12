from mite_data.modules.metadata_manager import MetadataManager


def test_init_valid():
    assert isinstance(MetadataManager(), MetadataManager)


def test_collect_metadata():
    manager = MetadataManager()
    manager.collect_metadata()
    assert manager.metadata_as.get("entries", {}).get("MITE0000001", None) is not None
    assert manager.metadata_mibig.get("entries", {}).get("BGC0000026", None) is not None
