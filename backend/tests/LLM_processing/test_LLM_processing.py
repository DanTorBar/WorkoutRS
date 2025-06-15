# Tests para LLM_processing
import pytest
from main.LLM_processing.LLM_processing import generar_equipamiento
from main.LLM_processing.translator_module import manual_translate, translate_text

def test_LLM_processing_placeholder():
    assert True

def test_generar_equipamiento(monkeypatch):
    # Mock del pipeline de HuggingFace
    class DummyGen:
        def __call__(self, prompt, max_length):
            return [{"generated_text": "Mancuernas, Banco"}]
    monkeypatch.setattr("main.LLM_processing.LLM_processing.generator", DummyGen())
    nombre = "Press banca"
    instrucciones = "Acostado en banco, empuja la barra hacia arriba."
    equipamiento = generar_equipamiento(nombre, instrucciones)
    assert "Mancuernas" in equipamiento or "Banco" in equipamiento

def test_generar_equipamiento_mock(monkeypatch):
    class DummyGen:
        def __call__(self, prompt, max_length):
            return [{"generated_text": "Mancuernas, Banco"}]
    monkeypatch.setattr("main.LLM_processing.LLM_processing.generator", DummyGen())
    nombre = "Press banca"
    instrucciones = "Acostado en banco, empuja la barra hacia arriba."
    equipamiento = generar_equipamiento(nombre, instrucciones)
    assert "Mancuernas" in equipamiento or "Banco" in equipamiento

def test_manual_translate_cases():
    assert manual_translate("Thighs") == "Muslos"
    assert manual_translate("No existe") is None
