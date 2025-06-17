from main.recommendations.recommendation_evaluator import evaluate_recommendations_for_users
import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from main.recommendations.recommender import (
    recommend_exercises, recommend_workouts, penalize, get_cached_recommendations, init_recommender
)
from main.models.users import HealthProfile
from main.models.exercise import Exercise
from main.models.workout import Workout
from django.contrib.auth.models import User

@pytest.fixture
def mock_profile():
    profile = MagicMock(spec=HealthProfile)
    profile.get_goals_list.return_value = ['Pérdida de peso']
    profile.get_conditions_list.return_value = ['Artritis']
    profile.get_equipment_list.return_value = ['Mancuernas', 'Banco']
    profile.get_environment_list.return_value = ['Casa']
    profile.height_cm = 170
    profile.weight_kg = 80
    profile.date_of_birth = None
    profile.cardio_vig_level = 0
    profile.imported_cardio_vig_min = 0
    profile.imported_cardio_mod_min = 0
    return profile

@pytest.fixture
def mock_exercise():
    ex = MagicMock(spec=Exercise)
    ex.exerciseCategory = 'Cardio,Correr'
    ex.equipment = 'Mancuernas,Banco'
    return ex

@pytest.fixture
def mock_workout():
    wk = MagicMock(spec=Workout)
    wk.workoutCategory = 'Entrenamiento en circuito'
    return wk

def test_penalize_condition(mock_profile, mock_exercise):
    score = penalize(mock_profile, mock_exercise, 1.0, is_ex=True)
    assert score < 1.0  # Penaliza por condición 'Artritis'

def test_penalize_equipment_missing(mock_profile, mock_exercise):
    mock_profile.get_equipment_list.return_value = ['Banco']
    score = penalize(mock_profile, mock_exercise, 1.0, is_ex=True)
    assert score < 1.0  # Penaliza por faltar 'Mancuernas'

def test_penalize_no_penalty(mock_profile, mock_exercise):
    mock_profile.get_conditions_list.return_value = []
    mock_profile.get_equipment_list.return_value = ['Mancuernas', 'Banco']
    score = penalize(mock_profile, mock_exercise, 1.0, is_ex=True)
    assert score == 1.0

def test_penalize_workout_condition(mock_profile, mock_workout):
    score = penalize(mock_profile, mock_workout, 1.0, is_ex=False)
    assert score < 1.0  # Penaliza por condición en workout

@patch('main.recommendations.recommender.get_cached_recommendations')
def test_recommend_exercises_uses_cache(mock_cache):
    mock_cache.return_value = pd.DataFrame({'id': [1], 'exerciseName': ['Test']})
    result = recommend_exercises(1, top_n=1)
    assert not result.empty
    assert result.iloc[0]['exerciseName'] == 'Test'

@patch('main.recommendations.recommender.get_cached_recommendations')
def test_recommend_workouts_uses_cache(mock_cache):
    mock_cache.return_value = pd.DataFrame({'id': [1], 'workoutName': ['Rutina']})
    result = recommend_workouts(1, top_n=1)
    assert not result.empty
    assert result.iloc[0]['workoutName'] == 'Rutina'

from main.models.recommendations import RecommendCache

@pytest.mark.django_db
@patch('main.recommendations.recommender.init_recommender')
def test_init_recommender_called_if_needed(mock_init):
    # Limpia la caché para asegurar que no hay resultados previos
    RecommendCache.objects.filter(user_id=1, item_type='exercise').delete()
    import builtins
    if hasattr(builtins, 'df_ex'):
        del builtins.df_ex
    if hasattr(builtins, 'df_wk'):
        del builtins.df_wk
    try:
        recommend_exercises(1, top_n=1)
    except Exception:
        pass
    mock_init.assert_called()

def test_penalize_score_not_negative(mock_profile, mock_exercise):
    score = penalize(mock_profile, mock_exercise, -5.0, is_ex=True)
    assert score == 0.0

# Puedes añadir más tests para edge cases, cold start, y lógica de penalización avanzada.

@pytest.mark.django_db
def test_evaluator_returns_recommendations():
    # Crea usuario y perfil
    user = User.objects.create_user(username="testuser", password="testpass")
    HealthProfile.objects.create(user=user, gender="masculino", height_cm=180, weight_kg=75)
    # Crea ejercicios y rutinas
    Exercise.objects.create(exerciseName="Sentadilla", exerciseCategory="Piernas", equipment="Mancuernas")
    Exercise.objects.create(exerciseName="Press banca", exerciseCategory="Pecho", equipment="Banco")
    Workout.objects.create(workoutName="Full Body", workoutCategory="Fuerza", level="1", gender="masculino", bodyPart="Piernas", description="Rutina completa")
    Workout.objects.create(workoutName="Cardio Express", workoutCategory="Cardio", level="2", gender="femenino", bodyPart="Piernas", description="Rutina de cardio")
    # Llama al evaluador
    df_ex, df_wk = evaluate_recommendations_for_users(user_ids=[user.id], top_n=2)
    assert not df_ex.empty
    assert not df_wk.empty
    assert df_ex['user_id'].iloc[0] == user.id
    assert df_wk['user_id'].iloc[0] == user.id
