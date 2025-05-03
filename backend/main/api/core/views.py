# main/api/core/views.py

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from main.search.search import almacenar_datos
from main.models.workout import Workout
from main.models.exercise import Exercise


class PopulateDatabaseAPIView(APIView):
    """
    POST /api/v1/core/populate/
    Lanza la carga inicial de datos y devuelve un mensaje.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            mensaje = almacenar_datos()
            return Response({'mensaje': mensaje}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def recommend_workouts(id):
    # # Obtener todas las rutinas
    # rutinas = list(Workout.objects.all().values(
    #     "id", "workoutName", "workoutCategory", "level", "gender", "bodyPart", "description"
    # ))

    # # Obtener las recomendaciones
    # recomendaciones = calcular_similitud(rutinas, id, ["workoutName", "workoutCategory", "level", "gender", "bodyPart"], 5)

    # return recomendaciones
    return True

def recommend_exercises(id):
    # # Obtener todos los ejercicios
    # ejercicios = list(Exercise.objects.all().values(
    #     "id", "exerciseName", "exerciseCategory", "priMuscles", "secMuscles"
    # ))

    # # Obtener las recomendaciones
    # recomendaciones = calcular_similitud(ejercicios, id, ["exerciseName", "exerciseCategory", "exerciseCategory", "priMuscles", "secMuscles"], 5)

    # return recomendaciones
    return True

