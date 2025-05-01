from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from main.api.workoutRS.views import recommend_workouts
from main.api.workouts.serializers import WorkoutDetailSerializer, WorkoutSerializer
from main.models.workout import Workout, WorkoutExercise
from main.search.search import buscar_rutinas_por_nombre_descripcion, ru_buscar

class WorkoutViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer


class WorkoutSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get('name', '')
        workoutCategory = request.data.get('workoutCategory', '')
        level = request.data.get('level', '')
        gender = request.data.get('gender', '')
        order = request.data.get('order', 'name')

        # ru_buscar es tu función personalizada de búsqueda avanzada
        rutinas = ru_buscar(
            name=name,
            cat=workoutCategory if workoutCategory != "Seleccionar" else "",
            level=level if level != "N/A" else "",
            gender=gender if gender != "N/A" else "",
            user=request.user,
            order=order
        )

        serializer = WorkoutSerializer(rutinas, many=True)
        return Response(serializer.data)


class WorkoutTermSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        term = request.data.get('term', '')
        order = request.data.get('order', 'name')

        rutinas = buscar_rutinas_por_nombre_descripcion(term, user=request.user, order=order)
        serializer = WorkoutSerializer(rutinas, many=True)
        return Response(serializer.data)


class WorkoutDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        rutina = get_object_or_404(Workout, pk=pk)

        # Obtener los días con ejercicios
        days = []
        for day in range(1, 8):
            exercises = WorkoutExercise.objects.filter(workout=rutina, day=day).select_related('exercise')
            days.append({
                "day": day,
                "exercises": [we.exercise.exerciseName for we in exercises]
            })
        
        # Comprueba que el usuario está logueado
        
        # Recomendar rutinas
        rutinas_rec = recommend_workouts(pk)
        for ru in rutinas_rec:
            ru['idWorkout'] = ru.get('id')

        serializer = WorkoutDetailSerializer(rutina)

        return Response({
            'rutina': serializer.data,
            'days': days,
            'recommended': rutinas_rec
        })


def order_results(results, order):
    if order == 'name':
        results = sorted(results, key=lambda x: x.workoutName.lower())
    elif order == 'popularity':
        recent_period = now() - timedelta(days=14)
        for workout in results:
            recent_likes = workout.favourite_set.filter(date_added__gte=recent_period).count()
            workout.recent_likes = recent_likes
        results = sorted(results, key=lambda x: getattr(x, 'recent_likes', 0), reverse=True)
    elif order == 'likes_count':
        results = sorted(results, key=lambda x: x.likes_count, reverse=True)
    elif order == 'creationDate':
        results = sorted(results, key=lambda x: x.creationDate, reverse=True)
    return results
