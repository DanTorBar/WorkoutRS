import pytest
from main.data_transformation.equipment_classifier import classify_equipment

def test_casa_sin_equipamiento():
    res = classify_equipment('Flexiones', 'Haz flexiones en el suelo')
    assert res == 'Casa, Ninguno'

def test_gimnasio_con_mancuernas():
    res = classify_equipment('Curl de bíceps', 'Usa mancuernas para trabajar los bíceps')
    assert res == 'Casa, Mancuernas'

def test_gimnasio_con_maquinas():
    res = classify_equipment('Press de banca', 'Realiza el ejercicio en una máquina de press')
    assert res == 'Gimnasio, Máquinas'

def test_airelibre_con_cuerda():
    res = classify_equipment('Saltar cuerda', 'Hazlo al aire libre con una comba')
    assert res == 'AireLibre, CuerdaSaltadora'

def test_prioridad_casa():
    res = classify_equipment('Plancha', 'Ejercicio de core en casa, sin material')
    assert res == 'Casa, Ninguno'

def test_prioridad_gimnasio_sobre_airelibre():
    res = classify_equipment('Remo en máquina', 'Ejercicio en máquina en el gimnasio o al aire libre')
    assert res == 'Gimnasio, Máquinas'

def test_varios_equipos():
    res = classify_equipment('Entrenamiento mixto', 'Usa mancuernas, bandas elásticas y banco')
    assert res == 'Casa, Banco, BandasElásticas, Mancuernas'

def test_sin_keywords():
    res = classify_equipment('Ejercicio desconocido', 'Sin información relevante')
    assert res == 'Casa, Ninguno'
