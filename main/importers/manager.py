from django.core.exceptions import ValidationError, PermissionDenied

from main.models import ActivityLog, HealthProfile
from .garmin.importer import GarminImporter
from .fitbit.importer import FitbitImporter
from .apple.importer import AppleImporter
from .googlefit.importer import GoogleFitImporter
# importa el resto...

IMPORTERS = {
    'garmin': GarminImporter,
    'fitbit': FitbitImporter,
    'apple': AppleImporter,
    'googlefit': GoogleFitImporter,
    # 'samsung': SamsungImporter,
    # 'zepp': ZeppImporter,
}


def import_health_data(user, file_obj, source_key):
    # Verifica si el usuario tiene consentimiento para importar datos de salud
    consent = getattr(user, 'health_data_consent', None)
    if not consent or not consent.given:
        raise PermissionDenied("No tienes permiso para importar datos de salud sin consentimiento.")

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

    
    # Log de importación
    ActivityLog.objects.create(
        user=user,
        action='IMPORT',
        detail=f"Imported from {source_key}: {profile}"
    )

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
