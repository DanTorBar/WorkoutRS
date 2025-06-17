# Tests para translator_module
import pytest
from main.data_transformation.translator_module import manual_translate
from main.data_transformation import translator_module

def test_translator_module_placeholder():
    assert True

@pytest.mark.parametrize("term,expected", [
    ("Thighs", "Muslos"),
    ("Chest", "Pecho"),
    ("N/A", "N/A"),
    ("No existe", None),
])
def test_manual_translate(term, expected):
    assert manual_translate(term) == expected

# Nota: Para testear translate_text con DeepL real, se recomienda mockear deepl_client

def test_translate_text_handles_error(monkeypatch):
    from main.data_transformation import translator_module
    def fake_deepl(*a, **kw):
        raise Exception("fail")
    monkeypatch.setattr(translator_module, "deepl", fake_deepl)
    # Si la función lanza, debe propagar o devolver el texto original
    assert translator_module.translate_text("prueba") == "prueba"

def test_translate_text_handles_error(monkeypatch):
    def fake_deepl(*a, **kw):
        raise Exception("fail")
    monkeypatch.setattr(translator_module, "deepl", fake_deepl)
    # Si la función lanza, debe propagar o devolver el texto original
    assert translator_module.translate_text("prueba") == "prueba"
