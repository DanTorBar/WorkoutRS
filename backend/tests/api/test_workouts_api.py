# Tests para endpoints y lógica de workouts
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from main.models.workout import Workout
from unittest.mock import patch
from main.api.workouts import views
from rest_framework.test import APIRequestFactory

User = get_user_model()

def test_workouts_placeholder():
    assert True

@pytest.mark.django_db
def test_workout_list_api():
    Workout.objects.create(workoutName="Rutina API", workoutCategory="", level="", gender="", bodyPart="", description="")
    with patch("main.search.search.ru_buscar", side_effect=lambda *a, **kw: list(Workout.objects.all())):
        client = APIClient()
        url = "/api/v1/workouts/"
        response = client.get(url)
    assert response.status_code == 200
    results = response.data.get("results", response.data)
    print("RESULTS:", results)
    if isinstance(results, dict):
        results = []
    assert any(w['workoutName'] == "Rutina API" for w in results)

@pytest.mark.django_db
def test_workout_create_api():
    client = APIClient()
    user = User.objects.create_user(username="apiuser2", password="testpass")
    client.force_authenticate(user=user)
    url = reverse('workout-list')  # Ajusta el nombre según tus urls
    data = {"workoutName": "Rutina Nueva"}
    response = client.post(url, data)
    assert response.status_code in (200, 201)
    assert Workout.objects.filter(workoutName="Rutina Nueva").exists()

@pytest.mark.django_db
def test_workout_list_returns_all():
    Workout.objects.create(workoutName="Rutina 1", workoutCategory="", level="", gender="", bodyPart="", description="")
    Workout.objects.create(workoutName="Rutina 2", workoutCategory="", level="", gender="", bodyPart="", description="")
    with patch("main.search.search.ru_buscar", side_effect=lambda *a, **kw: list(Workout.objects.all())):
        client = APIClient()
        url = "/api/v1/workouts/"
        response = client.get(url)
    assert response.status_code == 200
    results = response.data.get("results", response.data)
    print("RESULTS:", results)
    if isinstance(results, dict):
        results = []
    names = [w['workoutName'] for w in results]
    assert "Rutina 1" in names and "Rutina 2" in names

@pytest.mark.django_db
def test_workout_create_requires_auth():
    url = "/api/v1/workouts/"
    data = {"workoutName": "Rutina Nueva"}
    client = APIClient()
    response = client.post(url, data)
    assert response.status_code in (401, 403)

@pytest.mark.django_db
def test_workout_create_and_invalid():
    user = User.objects.create_user(username="apiuser2", password="testpass")
    client = APIClient()
    client.force_authenticate(user=user)
    url = "/api/v1/workouts/"
    # Caso válido
    data = {"workoutName": "Rutina Válida"}
    response = client.post(url, data)
    assert response.status_code in (200, 201)
    # Caso inválido (faltan campos obligatorios si los hay)
    data = {"workoutCategory": "Fuerza"}
    response = client.post(url, data)
    assert response.status_code in (400, 422)

@pytest.mark.django_db
def test_workout_options_returns_200():
    factory = APIRequestFactory()
    request = factory.get('/api/v1/workouts/options/')
    response = views.workout_options(request)
    assert response.status_code == 200

@pytest.mark.django_db
def test_workout_retrieve_authenticated():
    user = User.objects.create_user(username="testuser", password="testpass")
    workout = Workout.objects.create(workoutName="Rutina Retrieve", workoutCategory="", level="", gender="", bodyPart="", description="", creator=user)
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse('workout-detail', args=[workout.id])
    response = client.get(url)
    assert response.status_code == 200
    data = response.data
    assert 'workout' in data
    assert 'days' in data
    assert data['workout']['liked'] is False or data['workout']['liked'] is True

@pytest.mark.django_db
def test_workout_retrieve_unauthenticated():
    user = User.objects.create_user(username="testuser2", password="testpass")
    workout = Workout.objects.create(workoutName="Rutina Retrieve 2", workoutCategory="", level="", gender="", bodyPart="", description="", creator=user)
    client = APIClient()
    url = reverse('workout-detail', args=[workout.id])
    response = client.get(url)
    # Debe devolver 401 y un mensaje de error
    assert response.status_code in (401, 403)
    assert 'detail' in response.data
