import pytest
from main.search import search

def test_buscar_ejercicios_por_nombre_instrucciones_empty():
    result = search.buscar_ejercicios_por_nombre_instrucciones("", None)
    assert isinstance(result, list)

def test_ej_buscar_empty(monkeypatch):
    # Simula que no existe el índice Whoosh
    monkeypatch.setattr(search, "open_dir", lambda *a, **kw: (_ for _ in ()).throw(Exception("fail")))
    result = search.ej_buscar("", "", "", None, "")
    assert result == []

def test_ru_buscar_empty(monkeypatch):
    monkeypatch.setattr(search, "open_dir", lambda *a, **kw: (_ for _ in ()).throw(Exception("fail")))
    result = search.ru_buscar("", "", "", "", None)
    assert result == []
