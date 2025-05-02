# main/api/workouts/views.py

from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from main.models.workout import Workout, WorkoutExercise
from main.models.logs import ViewLog
from main.search.search import buscar_rutinas_por_nombre_descripcion, ru_buscar
from main.api.workouts.serializers import WorkoutSerializer, WorkoutDetailSerializer

from main.api.core.views import recommend_workouts  # ajusta import si cambió de ruta


class WorkoutViewSet(viewsets.ModelViewSet):
    """
    - list, create, retrieve, update, destroy de Workout
    - POST /api/v1/workouts/search/             → búsqueda avanzada
    - POST /api/v1/workouts/term-search/        → búsqueda por término en nombre/descr.
    - retrieve() incluye días y recomendaciones
    """
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer

    def get_permissions(self):
        if self.action in ('search', 'term_search'):
            return [IsAuthenticated()]
        if self.action == 'retrieve':
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        name = request.data.get('name', '')
        cat  = request.data.get('workoutCategory', '')
        level= request.data.get('level', '')
        gender = request.data.get('gender', '')
        order  = request.data.get('order', 'name')

        rutinas = ru_buscar(
            name=name,
            cat= '' if cat in ('Seleccionar', None) else cat,
            level= '' if level in ('N/A', None) else level,
            gender='' if gender in ('N/A', None) else gender,
            user=request.user,
            order=order
        )
        serializer = WorkoutSerializer(rutinas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='term-search')
    def term_search(self, request):
        term  = request.data.get('term', '')
        order = request.data.get('order', 'name')
        rutinas = buscar_rutinas_por_nombre_descripcion(term, user=request.user, order=order)
        serializer = WorkoutSerializer(rutinas, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/v1/workouts/{pk}/ → datos básicos + days + recommended
        """
        rutina = self.get_object()
        basic = WorkoutDetailSerializer(rutina).data

        # registrar la vista
        ViewLog.objects.create(
            user = request.user,
            content_type = ContentType.objects.get_for_model(instance),
            object_id = instance.pk
        )

        # Prepare days
        days = []
        for d in range(1, 8):
            exercises = WorkoutExercise.objects.filter(workout=rutina, day=d).select_related('exercise')
            days.append({
                'day': d,
                'exercises': [we.exercise.exerciseName for we in exercises]
            })

        # Recommendations
        recs = recommend_workouts(rutina.id)
        # añadimos idWorkout
        for r in recs:
            r['idWorkout'] = r.get('id') or r.get('idWorkout')

        return Response({
            'rutina': basic,
            'days': days,
            'recommended': recs
        }, status=status.HTTP_200_OK)
