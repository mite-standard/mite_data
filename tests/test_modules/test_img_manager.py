from mite_data.modules.img_manager import ImageManager


def test_init_valid():
    assert isinstance(ImageManager(), ImageManager)


def test_collect_uniprot_acc_valid():
    manager = ImageManager()
    manager.collect_uniprot_acc()
    assert not None in manager.uniprot_acc
    assert len(manager.uniprot_acc) != 0
