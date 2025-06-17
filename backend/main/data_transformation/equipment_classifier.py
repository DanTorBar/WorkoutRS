import re

# Opciones definidas en la aplicación
EQUIPMENT_CHOICES = [
    ("Casa", "Casa"),
    ("Gimnasio", "Gimnasio"),
    ("AireLibre", "Aire libre"),
    ("Mancuernas", "Mancuernas"),
    ("Barras", "Barras"),
    ("Máquinas", "Máquinas"),
    ("Poleas", "Poleas"),
    ("BandasElásticas", "Bandas elásticas"),
    ("Kettlebell", "Kettlebell"),
    ("TRX", "TRX"),
    ("Banco", "Banco"),
    ("Esterilla", "Esterilla"),
    ("CuerdaSaltadora", "Cuerda saltadora"),
    ("BalónMedicinal", "Balón medicinal"),
]

ENVIRONMENT_CHOICES = [
    ("Casa", "Casa"),
    ("Gimnasio", "Gimnasio"),
    ("AireLibre", "Aire libre"),
]

# Mappings de palabras clave a opciones
LOCATION_KEYWORDS = {
    'AireLibre': ['parque', 'al aire libre', 'correr', 'caminar', 'bicicleta', 'ciclismo'],
    'Gimnasio': ['máquina', 'gimnasio', 'polea', 'cruce de cables', 'press', 'peck deck', 'rack', 'multipower'],
    'Casa': ['flexiones', 'abdominales', 'plancha', 'sentadilla', 'puente', 'estiramiento', 'saltos', 'burpee']
}

EQUIPMENT_KEYWORDS = {
    'Banco': ['banco'],
    'Barras': ['barra', 'barra guiada'],
    'Mancuernas': ['mancuernas', 'mancuerna'],
    'Máquinas': ['máquina', 'prensa'],
    'Poleas': ['polea', 'cable', 'cruce de cables'],
    'BandasElásticas': ['bandas elásticas', 'bandas elasticas'],
    'Kettlebell': ['kettlebell'],
    'TRX': ['trx'],
    'Esterilla': ['esterilla', 'colchoneta'],
    'CuerdaSaltadora': ['cuerda saltadora', 'saltar cuerda', 'comba'],
    'BalónMedicinal': ['balón medicinal', 'medicinal'],
}


def classify_equipment(exercise_name: str, instructions: str) -> str:
    """
    Devuelve un único string con el entorno y equipamientos, separados por comas.
    El entorno es como máximo uno: Casa > Gimnasio > AireLibre.
    Si no se detecta entorno por keywords, se asigna Gimnasio si hay equipamiento de gimnasio,
    o Casa en caso contrario.
    """
    text = f"{exercise_name} {instructions}".lower()

    # Detectar entornos por keywords
    detected_locs = {key for key, kws in LOCATION_KEYWORDS.items() if any(w in text for w in kws)}

    # Detectar equipamiento específico
    detected_equips = {key for key, kws in EQUIPMENT_KEYWORDS.items() if any(w in text for w in kws)}

    # Determinar entorno cuando no hay keywords de lugar
    gym_equip = {'Barras', 'Máquinas', 'Poleas'}
    if not detected_locs:
        if detected_equips & gym_equip:
            env = 'Gimnasio'
        else:
            env = 'Casa'
    else:
        # Priorizar Casa > Gimnasio > AireLibre
        if 'Casa' in detected_locs:
            env = 'Casa'
        elif 'Gimnasio' in detected_locs:
            env = 'Gimnasio'
        else:
            env = 'AireLibre'

    # Preparar lista de equipamientos, o 'Ninguno'
    equips = sorted(detected_equips) if detected_equips else ['Ninguno']

    # Construir y devolver string final
    return ', '.join([env] + equips)