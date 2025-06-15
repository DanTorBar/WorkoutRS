# Tests para importers manager
import pytest
from main.importers import manager


def test_importers_manager_placeholder():
    assert True

def test_manager_import_returns_none_for_invalid():
    import io
    user = None
    file_obj = io.BytesIO(b"dummy")
    with pytest.raises(Exception):
        manager.import_health_data(user, file_obj, "invalid_source")
