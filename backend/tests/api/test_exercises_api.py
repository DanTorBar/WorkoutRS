# Tests para endpoints y lógica de exercises
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from main.models.exercise import Exercise, Muscle
from unittest.mock import patch

User = get_user_model()

@pytest.mark.django_db
def test_exercise_list_api():
    client = APIClient()
    Exercise.objects.create(exerciseName="Sentadilla", equipment="", exerciseCategory="")
    with patch("main.search.search.ej_buscar", return_value=Exercise.objects.all()):
        url = "/api/v1/exercises/"
        response = client.get(url)
    assert response.status_code == 200
    results = response.data.get("results", response.data)
    if isinstance(results, dict):
        results = []
    assert any(e.get('exerciseName') == "Sentadilla" for e in results)

@pytest.mark.django_db
def test_exercise_create_api():
    client = APIClient()
    user = User.objects.create_user(username="apiuser", password="testpass")
    client.force_authenticate(user=user)
    url = "/api/v1/exercises/"
    data = {"exerciseName": "Press banca", "equipment": "", "exerciseCategory": ""}
    response = client.post(url, data)
    assert response.status_code in (200, 201)
    assert Exercise.objects.filter(exerciseName="Press banca").exists()

@pytest.mark.django_db
def test_exercise_list_returns_all():
    Exercise.objects.create(exerciseName="Sentadilla", equipment="", exerciseCategory="")
    Exercise.objects.create(exerciseName="Press banca", equipment="", exerciseCategory="")
    with patch("main.search.search.ej_buscar", return_value=Exercise.objects.all()):
        client = APIClient()
        url = "/api/v1/exercises/"
        response = client.get(url)
    assert response.status_code == 200
    results = response.data.get("results", response.data)
    if isinstance(results, dict):
        results = []
    names = [e.get('exerciseName') for e in results]
    assert "Sentadilla" in names and "Press banca" in names

@pytest.mark.django_db
def test_exercise_create_requires_auth():
    url = "/api/v1/exercises/"
    data = {"exerciseName": "Dominadas", "equipment": "", "exerciseCategory": ""}
    client = APIClient()
    response = client.post(url, data)
    assert response.status_code in (401, 403)

@pytest.mark.django_db
def test_exercise_create_and_invalid():
    user = User.objects.create_user(username="apiuser", password="testpass")
    client = APIClient()
    client.force_authenticate(user=user)
    url = "/api/v1/exercises/"
    # Caso válido
    data = {"exerciseName": "Fondos", "equipment": "", "exerciseCategory": ""}
    response = client.post(url, data)
    assert response.status_code in (200, 201)
    # Caso inválido (faltan campos obligatorios si los hay)
    data = {"exerciseCategory": "Fuerza"}
    response = client.post(url, data)
    assert response.status_code in (400, 422)
