import pytest
import pandas as pd
from django.contrib.auth import get_user_model
from main.models.users import HealthProfile
from main.recommendations.recommender import init_recommender
from main.api import core as views

# @pytest.mark.django_db
# def test_recommend_exercises_returns_list():
#     User = get_user_model()
#     user = User.objects.create_user(username="testuser", password="testpass")
#     HealthProfile.objects.create(user=user, gender="masculino", height_cm=180, weight_kg=75)
#     from main.models.exercise import Exercise
#     Exercise.objects.all().delete()
#     Exercise.objects.create(exerciseName="Sentadilla profunda", exerciseCategory="Piernas", equipment="Mancuernas")
#     Exercise.objects.create(exerciseName="Press banca plano", exerciseCategory="Pecho", equipment="Banco")
#     Exercise.objects.create(exerciseName="Remo con barra", exerciseCategory="Espalda", equipment="Barras")
#     init_recommender()
#     result = views.recommend_exercises(user.id)
#     assert isinstance(result, pd.DataFrame)
#     assert not result.empty

# @pytest.mark.django_db
# def test_recommend_workouts_returns_list():
#     User = get_user_model()
#     user = User.objects.create_user(username="testuser2", password="testpass")
#     HealthProfile.objects.create(user=user, gender="masculino", height_cm=180, weight_kg=75)
#     from main.models.workout import Workout
#     Workout.objects.all().delete()
#     Workout.objects.create(workoutName="Full Body", workoutCategory="Fuerza", level="1", gender="masculino", bodyPart="Piernas", description="Rutina completa")
#     Workout.objects.create(workoutName="Cardio Express", workoutCategory="Cardio", level="2", gender="femenino", bodyPart="Piernas", description="Rutina de cardio")
#     Workout.objects.create(workoutName="Espalda y Core", workoutCategory="Fuerza", level="1", gender="masculino", bodyPart="Espalda", description="Rutina de core")
#     init_recommender()
#     result = views.recommend_workouts(user.id)
#     assert isinstance(result, pd.DataFrame)
#     assert not result.empty