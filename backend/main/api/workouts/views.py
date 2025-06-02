# main/api/workouts/views.py

from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.contenttypes.models import ContentType
from rest_framework.pagination import PageNumberPagination

from main.models.workout import Workout, WorkoutExercise
from main.models.logs import ViewLog
from main.models.social import Favourite
from main.search.search import buscar_rutinas_por_nombre_descripcion, ru_buscar
from main.api.workouts.serializers import WorkoutSerializer, WorkoutDetailSerializer

from main.api.core.views import recommend_workouts  # ajusta import si cambió de ruta


class WorkoutPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class WorkoutViewSet(viewsets.ModelViewSet):
    """
    - list, create, retrieve, update, destroy de Workout
    - POST /api/v1/workouts/search/             → búsqueda avanzada
    - POST /api/v1/workouts/term-search/        → búsqueda por término en nombre/descr.
    - retrieve() incluye días y recomendaciones
    """
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    pagination_class = WorkoutPagination

    def get_permissions(self):
        if self.action in ('list', 'search', 'term_search'):
            return [AllowAny()]
        return [IsAuthenticated()]

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

    def list(self, request, *args, **kwargs):
        name = request.query_params.get('term', '').strip()
        cat = request.query_params.get('cat', '').strip()
        level = request.query_params.get('level', '').strip()
        gender = request.query_params.get('gender', '').strip()
        order = request.query_params.get('order', 'name')
        # Usar siempre la función personalizada para que Whoosh gestione el filtrado y orden
        queryset = ru_buscar(name=name, user=request.user, order=order, cat=cat, level=level, gender=gender)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    # NOTA: En el frontend, para búsquedas, solo permite los valores de orden soportados por buscar_rutinas_por_nombre_descripcion: 'name', 'popularity', 'likes_count', 'creationDate'.

    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/v1/workouts/{pk}/ → datos básicos + days + recommended
        """
        workout = self.get_object()
        basic = WorkoutDetailSerializer(workout).data

        if request.user.is_authenticated:
            # registrar la vista
            ViewLog.objects.create(
                user=request.user,
                content_type=ContentType.objects.get_for_model(self.get_object()),
                object_id=self.get_object().pk
            )

            # Verificar si el usuario ya dio like
            liked = Favourite.objects.filter(user=request.user, workout=workout).exists()
        else:
            liked = False

        # Agregar el campo 'liked' a los datos básicos
        basic['liked'] = liked

        # Prepare days
        days = []
        for d in range(1, 8):
            exercises = WorkoutExercise.objects.filter(workout=workout, day=d).select_related('exercise')
            days.append({
                'day': d,
                'exercises': [we.exercise.exerciseName for we in exercises]
            })

        # Recommendations
        recs = recommend_workouts(workout.id)
        # añadimos idWorkout
        for r in recs:
            r['idWorkout'] = r.get('id') or r.get('idWorkout')

        return Response({
            'workout': basic,
            'days': days,
            'recommended': recs
        }, status=status.HTTP_200_OK)
