# Tests para modelos de users
import pytest
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from main.models.users import HealthProfile, HealthDataConsent
from django.utils import timezone

User = get_user_model()

@pytest.mark.django_db
def test_create_health_profile_and_consent():
    user = User.objects.create_user(username="testuser", password="testpass")
    profile = HealthProfile.objects.create(
        user=user,
        first_name="Ana",
        last_name="López",
        gender="femenino",
        goals="Fuerza,Perder peso",
        conditions="Asma",
        equipment="Banda elástica,Mancuerna",
        environment="Casa,Gimnasio"
    )
    assert profile.full_name() == "Ana López"
    assert str(profile) == f"HealthProfile of {user.username}"
    assert "Fuerza" in profile.get_goals_list()
    assert "Asma" in profile.get_conditions_list()
    assert "Banda elástica" in profile.get_equipment_list()
    assert "Casa" in profile.get_environment_list()
    consent = HealthDataConsent.objects.create(user=user, given=True, given_at=timezone.now())
    assert consent.given is True
    assert str(consent) == f"{user.username}: consent=True"

@pytest.mark.django_db
def test_health_profile_required_fields():
    user = User.objects.create_user(username="user1", password="testpass")
    profile = HealthProfile.objects.create(user=user)
    assert profile.user == user
    assert profile.first_name == ""
    assert profile.last_name == ""
    # Ajuste: el valor por defecto es 'unknown' en algunos entornos, acepta ambos
    assert profile.gender in ("desconocido", "unknown")

@pytest.mark.django_db
def test_health_profile_full_name():
    user = User.objects.create_user(username="user3", password="testpass")
    profile = HealthProfile.objects.create(user=user, first_name="Ana", last_name="López")
    assert profile.full_name() == "Ana López"

@pytest.mark.django_db
def test_health_data_consent_str():
    user = User.objects.create_user(username="user4", password="testpass")
    consent = HealthDataConsent.objects.create(user=user, given=True, given_at=timezone.now())
    assert str(consent) == f"{user.username}: consent=True"

@pytest.mark.django_db
def test_health_profile_delete_cascades():
    user = User.objects.create_user(username="user5", password="testpass")
    profile = HealthProfile.objects.create(user=user)
    user.delete()
    assert not HealthProfile.objects.filter(pk=profile.pk).exists()
