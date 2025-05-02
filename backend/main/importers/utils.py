# health/importers/utils.py

from dateutil import parser

def parse_date(val):
    if not val:
        return None
    try:
        return parser.parse(val).date()
    except (ValueError, TypeError):
        return None

def parse_float(val):
    """
    Intenta convertir a float. Devuelve None si falla.
    """
    try:
        return float(val)
    except (TypeError, ValueError):
        return None

def parse_gender(val):
    val = val.strip().upper() if val else None
    if val == "MALE" or val == "M":
        return 'MASCULINO'
    elif val == "FEMALE" or val == "F":
        return 'FEMENINO'
    else:
        return 'DESCONOCIDO'
