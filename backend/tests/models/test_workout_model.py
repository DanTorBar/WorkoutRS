# Tests para modelos de workout
import pytest
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from main.models.workout import Workout, WorkoutExercise
from main.models.exercise import Exercise

User = get_user_model()

@pytest.mark.django_db
def test_create_workout():
    user = User.objects.create_user(username="workoutuser", password="testpass")
    workout = Workout.objects.create(
        creator=user,
        workoutName="Rutina A",
        workoutCategory="Fuerza",
        level="Principiante",
        gender="Hombre",
        bodyPart="Pecho",
        description="Rutina de fuerza para pecho"
    )
    assert workout.workoutName == "Rutina A"
    assert str(workout) == "Rutina A"
    assert workout.creator == user

@pytest.mark.django_db
def test_create_workout_exercise():
    user = User.objects.create_user(username="workoutuser2", password="testpass")
    workout = Workout.objects.create(creator=user, workoutName="Rutina B")
    exercise = Exercise.objects.create(exerciseName="Press banca")
    we = WorkoutExercise.objects.create(workout=workout, exercise=exercise, day=1)
    assert we.workout == workout
    assert we.exercise == exercise
    assert str(we) == f"{workout.workoutName} - {exercise.exerciseName}"

@pytest.mark.django_db
def test_workout_required_fields():
    user = User.objects.create_user(username="wuser1", password="testpass")
    workout = Workout.objects.create(creator=user, workoutName="Rutina Test")
    assert workout.creator == user
    assert workout.workoutName == "Rutina Test"
    assert workout.likes_count == 0

@pytest.mark.django_db
def test_workout_str_and_ordering():
    user = User.objects.create_user(username="wuser2", password="testpass")
    Workout.objects.create(creator=user, workoutName="B")
    Workout.objects.create(creator=user, workoutName="A")
    names = list(Workout.objects.values_list("workoutName", flat=True))
    assert names == sorted(names)

@pytest.mark.django_db
def test_workout_exercise_unique_together():
    user = User.objects.create_user(username="wuser3", password="testpass")
    workout = Workout.objects.create(creator=user, workoutName="Rutina X")
    exercise = Exercise.objects.create(exerciseName="Press banca")
    WorkoutExercise.objects.create(workout=workout, exercise=exercise, day=1)
    with pytest.raises(IntegrityError):
        WorkoutExercise.objects.create(workout=workout, exercise=exercise, day=1)

@pytest.mark.django_db
def test_workout_exercise_str():
    user = User.objects.create_user(username="wuser4", password="testpass")
    workout = Workout.objects.create(creator=user, workoutName="Rutina Y")
    exercise = Exercise.objects.create(exerciseName="Sentadilla")
    we = WorkoutExercise.objects.create(workout=workout, exercise=exercise, day=2)
    assert str(we) == f"{workout.workoutName} - {exercise.exerciseName}"
