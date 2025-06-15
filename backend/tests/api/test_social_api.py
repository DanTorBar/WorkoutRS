# Tests para endpoints y lógica de social
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from main.models.social import Favourite
from main.models.workout import Workout
from main.models.exercise import Exercise

User = get_user_model()

def test_social_placeholder():
    assert True

@pytest.mark.django_db
def test_favourite_workout_api():
    client = APIClient()
    user = User.objects.create_user(username="apiuser4", password="testpass")
    workout = Workout.objects.create(creator=user, workoutName="Rutina Social")
    client.force_authenticate(user=user)
    url = reverse('favourite-list')  # Ajusta el nombre según tus urls
    data = {"workout": workout.id}
    response = client.post(url, data)
    assert response.status_code in (200, 201)
    assert Favourite.objects.filter(user=user, workout=workout).exists()

@pytest.mark.django_db
def test_favourite_requires_auth():
    url = "/api/v1/social/favourites/"
    client = APIClient()
    response = client.post(url, {})
    assert response.status_code in (401, 403)

@pytest.mark.django_db
def test_favourite_create_and_delete():
    user = User.objects.create_user(username="apiuser4", password="testpass")
    workout = Workout.objects.create(creator=user, workoutName="Rutina Social")
    client = APIClient()
    client.force_authenticate(user=user)
    url = "/api/v1/social/favourites/"
    data = {"workout": workout.id}
    response = client.post(url, data)
    assert response.status_code in (200, 201)
    fav_id = response.data.get('id')
    # Eliminar favorito
    del_url = f"/api/v1/social/favourites/{fav_id}/"
    del_response = client.delete(del_url)
    assert del_response.status_code in (200, 204)
    assert not Favourite.objects.filter(id=fav_id).exists()
