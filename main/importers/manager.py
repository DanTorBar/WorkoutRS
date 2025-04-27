from django.core.exceptions import ValidationError, PermissionDenied

from main.models import ActivityLog
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
    # from models import HealthProfile
    # HealthProfile.objects.update_or_create(
    #     user=user,
    #     defaults=parsed
    # )
    
    # Log de importación
    ActivityLog.objects.create(
        user=user,
        action='IMPORT',
        detail=f"Imported from {source_key}: {parsed}"
    )

    return parsed