import pytest
from main.api.core import views
from rest_framework.test import APIRequestFactory

@pytest.mark.django_db
def test_recommend_exercises_returns_list():
    # Simula un ejercicio existente
    from main.models.exercise import Exercise
    e = Exercise.objects.create(exerciseName="Test", equipment="", exerciseCategory="")
    result = views.recommend_exercises(e.id)
    assert isinstance(result, list)

@pytest.mark.django_db
def test_recommend_workouts_returns_list():
    from main.models.workout import Workout
    w = Workout.objects.create(workoutName="TestW", workoutCategory="", level="", gender="", bodyPart="", description="")
    result = views.recommend_workouts(w.id)
    assert isinstance(result, list)
