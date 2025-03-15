from main.models import Exercise, Workout
from main.recommendations.recommendations import calcular_similitud


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