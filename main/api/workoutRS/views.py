from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from main.models.exercise import Exercise
from main.models.workout import Workout
from main.search.search import almacenar_datos
from django.shortcuts import render
from main.recommendations.recommendations import calcular_similitud


def index(request):
    return render(request, 'index.html',{'STATIC_URL':settings.STATIC_URL})

def populateDatabase(request):
    mensaje = almacenar_datos()
    return JsonResponse({'mensaje': mensaje})

# Recomendaciones

def recommend_workouts(id):
    # Obtener todas las rutinas
    rutinas = list(Workout.objects.all().values(
        "id", "workoutName", "workoutCategory", "level", "gender", "bodyPart", "description"
    ))

    # Obtener las recomendaciones
    recomendaciones = calcular_similitud(rutinas, id, ["workoutName", "workoutCategory", "level", "gender", "bodyPart"], 5)

    return recomendaciones

def recommend_exercises(id):
    # Obtener todos los ejercicios
    ejercicios = list(Exercise.objects.all().values(
        "id", "exerciseName", "exerciseCategory", "priMuscles", "secMuscles"
    ))

    # Obtener las recomendaciones
    recomendaciones = calcular_similitud(ejercicios, id, ["exerciseName", "exerciseCategory", "exerciseCategory", "priMuscles", "secMuscles"], 5)

    return recomendaciones