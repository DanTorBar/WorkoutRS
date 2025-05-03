# health/tasks.py

from celery import shared_task
from django.contrib.auth import get_user_model

from main.models.users import HealthDataConsent, HealthProfile
from main.models.logs import ActivityLog

User = get_user_model()

@shared_task
def revoke_health_data(user_id):
    """
    Borra o anonimiza todos los datos de salud del usuario:
     - Profile de salud
     - Consentimiento
     - ActivityLog (opcionales)
     - Cualquier otro modelo asociado
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return f"Usuario {user_id} no existe."

    # 1) Borrar perfil de salud
    HealthProfile.objects.filter(user=user).delete()

    # 2) Resetear consentimiento
    HealthDataConsent.objects.filter(user=user).update(given=False, given_at=None)

    # 3) Log de borrado
    ActivityLog.objects.create(
        user=user,
        action='DELETE',
        detail="Revocación de consentimiento: borrado de datos de salud."
    )

    # 4) (Opcional) Borrar logs de importación previos
    # ActivityLog.objects.filter(user=user, action='IMPORT').delete()

    return f"Datos de salud de {user.username} borrados."
