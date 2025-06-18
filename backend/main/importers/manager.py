from django.core.exceptions import ValidationError, PermissionDenied

from main.models.users import HealthProfile
from main.models.logs import ActivityLog

from main.importers.garmin.importer import GarminImporter
from main.importers.fitbit.importer import FitbitImporter
from main.importers.apple.importer import AppleImporter
from main.importers.googlefit.importer import GoogleFitImporter

IMPORTERS = {
    'garmin': GarminImporter,
    'fitbit': FitbitImporter,
    'apple': AppleImporter,
    'googlefit': GoogleFitImporter,
}


def import_health_data(user, file_obj, source_key):

    cls = IMPORTERS.get(source_key.lower())
    if not cls:
        raise ValidationError(f"Origen no soportado: {source_key}")
    importer = cls(file_obj)
    parsed = importer.parse()
    
    profile, created = HealthProfile.objects.update_or_create(
        user=user,
        defaults=parsed
    )

    # Ahora asignamos los niveles manuales según los minutos importados:
    # Solo sobrescribimos si vinieron datos automáticos:
    if parsed.get('imported_neat_min') is not None:
        profile.neat_level = minutes_to_level(parsed['imported_neat_min'])
    if parsed.get('imported_cardio_mod_min') is not None:
        profile.cardio_mod_level = minutes_to_level(parsed['imported_cardio_mod_min'])
    if parsed.get('imported_cardio_vig_min') is not None:
        profile.cardio_vig_level = minutes_to_level(parsed['imported_cardio_vig_min'])
    if parsed.get('imported_strength_min') is not None:
        profile.strength_level = minutes_to_level(parsed['imported_strength_min'])

    profile.save()

    return parsed


def preparse_health_data(file_obj, source_key):
    cls = IMPORTERS.get(source_key.lower())
    if not cls:
        raise ValidationError(f"Origen no soportado: {source_key}")
    importer = cls(file_obj)
    parsed = importer.parse()

    # Asigna los niveles manuales según los minutos importados (igual que import_health_data, pero solo en el dict)
    if parsed.get('imported_neat_min') is not None:
        parsed['neat_level'] = minutes_to_level(parsed['imported_neat_min'])
    if parsed.get('imported_cardio_mod_min') is not None:
        parsed['cardio_mod_level'] = minutes_to_level(parsed['imported_cardio_mod_min'])
    if parsed.get('imported_cardio_vig_min') is not None:
        parsed['cardio_vig_level'] = minutes_to_level(parsed['imported_cardio_vig_min'])
    if parsed.get('imported_strength_min') is not None:
        parsed['strength_level'] = minutes_to_level(parsed['imported_strength_min'])

    return parsed


def minutes_to_level(minutes: int) -> int:
    """
    Convierte minutos semanales en un nivel de actividad de 1 a 5.
    
    Umbrales por defecto:
      - Nivel 1: 0   –  60 min/semana
      - Nivel 2: 61  – 120 min/semana
      - Nivel 3: 121 – 180 min/semana
      - Nivel 4: 181 – 240 min/semana
      - Nivel 5: > 240 min/semana
    """
    if minutes <= 60:
        return 1
    elif minutes <= 120:
        return 2
    elif minutes <= 180:
        return 3
    elif minutes <= 240:
        return 4
    else:
        return 5
