import pytest
from main.LLM_processing import translator_module

def test_translate_text_handles_error(monkeypatch):
    def fake_deepl(*a, **kw):
        raise Exception("fail")
    monkeypatch.setattr(translator_module, "deepl", fake_deepl)
    # Si la función lanza, debe propagar o devolver el texto original
    assert translator_module.translate_text("prueba") == "prueba"
