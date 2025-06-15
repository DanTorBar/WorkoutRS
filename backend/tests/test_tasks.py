import pytest
from main.models.exercise import Exercise
from main.models.workout import Workout
from main.models.social import Favourite
from main.models.users import HealthProfile
from main.tasks import revoke_health_data
from django.contrib.auth import get_user_model
from main.models.users import HealthDataConsent
from main.models.logs import ActivityLog

User = get_user_model()

# Pruebas para backend/main/tasks.py

def test_dummy():
    assert True

@pytest.mark.django_db
def test_revoke_health_data_deletes_profile_and_resets_consent():
    user = User.objects.create_user(username="celeryuser", password="testpass")
    profile = HealthProfile.objects.create(user=user, first_name="Celery", last_name="Test")
    # Consentimiento
    consent = HealthDataConsent.objects.create(user=user, given=True)
    # Ejecutar tarea
    revoke_health_data(user.id)
    assert not HealthProfile.objects.filter(user=user).exists()
    consent.refresh_from_db()
    assert consent.given is False

@pytest.mark.django_db
def test_revoke_health_data_task():
    user = User.objects.create_user(username="celeryuser", password="testpass")
    profile = HealthProfile.objects.create(user=user)
    consent = HealthDataConsent.objects.create(user=user, given=True)
    revoke_health_data(user.id)
    assert not HealthProfile.objects.filter(user=user).exists()
    consent.refresh_from_db()
    assert consent.given is False

@pytest.mark.django_db
def test_revoke_health_data_user_not_exist():
    result = revoke_health_data(99999)
    assert "no existe" in result

@pytest.mark.django_db
def test_revoke_health_data_success():
    user = User.objects.create_user(username="testuser", password="testpass")
    HealthProfile.objects.create(user=user)
    HealthDataConsent.objects.create(user=user, given=True)
    result = revoke_health_data(user.id)
    assert "borrados" in result or "borrado" in result
    assert not HealthProfile.objects.filter(user=user).exists()
    assert not HealthDataConsent.objects.filter(user=user, given=True).exists()
    assert ActivityLog.objects.filter(user=user, action='DELETE').exists()
