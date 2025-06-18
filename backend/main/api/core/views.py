# main/api/core/views.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from main.search.search import almacenar_datos
from main.recommendations.recommender import recommend_exercises, recommend_workouts
from main.api.core.serializers import RecommendedWorkoutSerializer, RecommendedExerciseSerializer
from main.models.exercise import Exercise
from main.models.workout import Workout


class PopulateDatabaseAPIView(APIView):
    """
    POST /api/v1/core/populate/
    Lanza la carga inicial de datos y devuelve un mensaje.
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        try:
            mensaje = almacenar_datos()
            return Response({'mensaje': mensaje}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecommendExercisesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        df = recommend_exercises(user_id, top_n=5)
        exercises = Exercise.objects.filter(id__in=df['id'].tolist())
        serialized = RecommendedExerciseSerializer(exercises, many=True)
        return Response(serialized.data)


class RecommendWorkoutsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        df = recommend_workouts(user_id, top_n=5)
        workouts = Workout.objects.filter(id__in=df['id'].tolist())
        serialized = RecommendedWorkoutSerializer(workouts, many=True)
        return Response(serialized.data)

