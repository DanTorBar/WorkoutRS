# Tests para modelos de exercise
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from main.models.exercise import Muscle, Exercise

@pytest.mark.django_db
def test_create_muscle():
    muscle = Muscle.objects.create(name="Bíceps")
    assert muscle.name == "Bíceps"
    assert str(muscle) == "Bíceps"

@pytest.mark.django_db
def test_create_exercise():
    muscle1 = Muscle.objects.create(name="Bíceps")
    muscle2 = Muscle.objects.create(name="Tríceps")
    exercise = Exercise.objects.create(
        exerciseName="Curl de bíceps",
        exerciseCategory="Fuerza",
        video="https://example.com/video",
        instructions="Levanta la mancuerna",
        equipment="Mancuerna",
    )
    exercise.priMuscles.add(muscle1)
    exercise.secMuscles.add(muscle2)
    assert exercise.exerciseName == "Curl de bíceps"
    assert str(exercise) == "Curl de bíceps"
    assert muscle1 in exercise.priMuscles.all()
    assert muscle2 in exercise.secMuscles.all()

@pytest.mark.django_db
def test_exercise_ordering():
    Exercise.objects.create(exerciseName="A", exerciseCategory="Fuerza")
    Exercise.objects.create(exerciseName="B", exerciseCategory="Fuerza")
    names = list(Exercise.objects.values_list("exerciseName", flat=True))
    assert names == sorted(names)

@pytest.mark.django_db
def test_muscle_name_unique():
    Muscle.objects.create(name="Bíceps")
    with pytest.raises(IntegrityError):
        Muscle.objects.create(name="Bíceps")

@pytest.mark.django_db
def test_exercise_many_to_many_relations():
    m1 = Muscle.objects.create(name="Bíceps")
    m2 = Muscle.objects.create(name="Tríceps")
    ex = Exercise.objects.create(exerciseName="Curl", exerciseCategory="Fuerza")
    ex.priMuscles.add(m1)
    ex.secMuscles.add(m2)
    assert m1 in ex.priMuscles.all()
    assert m2 in ex.secMuscles.all()

@pytest.mark.django_db
def test_exercise_null_fields():
    ex = Exercise.objects.create(exerciseName="Sentadilla")
    assert ex.exerciseCategory is None
    assert ex.video is None
    assert ex.instructions is None
    assert ex.equipment is None

@pytest.mark.django_db
def test_exercise_str():
    ex = Exercise.objects.create(exerciseName="Press banca")
    assert str(ex) == "Press banca"

@pytest.mark.django_db
def test_exercise_ordering():
    Exercise.objects.create(exerciseName="B")
    Exercise.objects.create(exerciseName="A")
    names = list(Exercise.objects.values_list("exerciseName", flat=True))
    assert names == sorted(names)

@pytest.mark.django_db
def test_likes_count_non_negative():
    ex = Exercise.objects.create(exerciseName="Test", likes_count=0)
    ex.likes_count = 5
    ex.save()
    assert ex.likes_count == 5
    # Django PositiveIntegerField no permite negativos a nivel de base de datos, pero no valida en Python
    ex.likes_count = -1
    with pytest.raises(Exception):
        ex.save()
