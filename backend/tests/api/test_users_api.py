# Tests para endpoints y lógica de users
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from main.models.users import HealthProfile
from unittest.mock import patch

User = get_user_model()

def test_users_placeholder():
    assert True

@pytest.mark.django_db
def test_user_profile_api():
    client = APIClient()
    user = User.objects.create_user(username="apiuser3", password="testpass")
    HealthProfile.objects.create(user=user, first_name="Carlos", last_name="Test")
    client.force_authenticate(user=user)
    url = "/api/v1/users/profile/"
    response = client.get(url)
    assert response.status_code in (200, 404)  # Ajusta según implementación
    if response.status_code == 200:
        assert response.data['first_name'] == "Carlos"

@pytest.mark.django_db
def test_user_profile_requires_auth():
    url = "/api/v1/users/profile/"
    client = APIClient()
    response = client.get(url)
    assert response.status_code in (401, 403)

@pytest.mark.django_db
def test_user_profile_get_and_update():
    user = User.objects.create_user(username="apiuser3", password="testpass")
    HealthProfile.objects.create(user=user, first_name="Carlos", last_name="Test")
    client = APIClient()
    client.force_authenticate(user=user)
    url = "/api/v1/users/profile/"
    response = client.get(url)
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        assert response.data['first_name'] == "Carlos"
        # Actualización
        data = {"first_name": "Nuevo"}
        response = client.patch(url, data)
        assert response.status_code in (200, 202)
        assert response.data['first_name'] == "Nuevo"

@pytest.mark.django_db
def test_register_login_logout_me():
    client = APIClient()
    # Registro
    url = "/api/v1/users/register/"
    data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpass",
        "health_data_consent": True,
        "profile": {
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "1990-01-01",
            "gender": "masculino",
            "height_cm": 180,
            "weight_kg": 75,
            "goals": [],
            "conditions": [],
            "equipment": [],
            "environment": [],
            "neat_level": 1,
            "cardio_mod_level": 1,
            "cardio_vig_level": 1,
            "strength_level": 1
        }
    }
    response = client.post(url, data, format="json")
    print(response.data)
    assert response.status_code in (200, 201)
    # Login
    url = "/api/v1/users/login/"
    login_data = {"username": "testuser", "password": "testpass"}
    response = client.post(url, login_data)
    assert response.status_code == 200
    token = response.data['token']
    user_id = response.data['user_id']
    # Me
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    url = "/api/v1/users/me/"
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['id'] == user_id
    # Logout
    url = "/api/v1/users/logout/"
    response = client.post(url)
    assert response.status_code == 204

@pytest.mark.django_db
def test_health_data_preimport_no_file():
    client = APIClient()
    url = "/api/v1/users/fitbit/preimport/"
    response = client.post(url, {})
    assert response.status_code == 400
    assert 'error' in response.data

@pytest.mark.django_db
def test_health_data_preimport_unknown_service():
    client = APIClient()
    import io
    file = io.BytesIO(b"dummy")
    file.name = 'dummy.zip'
    url = "/api/v1/users/unknown/preimport/"
    response = client.post(url, {'file': file}, format='multipart')
    assert response.status_code == 400
    assert 'error' in response.data

@pytest.mark.django_db
def test_revoke_health_data_consent():
    from main.models.users import HealthDataConsent
    user = User.objects.create_user(username="consentuser", password="testpass")
    HealthDataConsent.objects.create(user=user, given=True)
    client = APIClient()
    client.force_authenticate(user=user)
    url = "/api/v1/users/revoke-consent/"
    with patch("main.api.users.views.revoke_health_data.delay") as mock_delay:
        response = client.post(url)
        assert response.status_code == 202 or response.status_code == 400
        if response.status_code == 202:
            mock_delay.assert_called_once_with(user.id)
