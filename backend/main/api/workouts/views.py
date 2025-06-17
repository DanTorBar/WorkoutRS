# main/api/workouts/views.py

from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.contenttypes.models import ContentType
from rest_framework.pagination import PageNumberPagination

from main.models.workout import Workout, WorkoutExercise
from main.models.exercise import Muscle
from main.models.logs import ViewLog
from main.models.social import Favourite
from main.search.search import buscar_rutinas_por_nombre_descripcion, ru_buscar
from main.api.workouts.serializers import WorkoutSerializer, WorkoutDetailSerializer

from main.api.core.views import recommend_workouts


class WorkoutPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class WorkoutViewSet(viewsets.ModelViewSet):
    """
    - list, create, retrieve, update, destroy de Workout
    - GET /api/v1/workouts/?page=X&page_size=12&term=Y&level=Z&order=name             → búsqueda avanzada (list)
    - retrieve() incluye días y recomendaciones
    """
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    pagination_class = WorkoutPagination

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

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

        return Response({
            'workout': basic,
            'days': days
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def workout_options(request):
    categories = set(Workout.objects.values_list('workoutCategory', flat=True).distinct())
    levels = set(Workout.objects.values_list('level', flat=True).distinct())
    genders = set(Workout.objects.values_list('gender', flat=True).distinct())
    return Response({
        'categories': sorted([c for c in categories if c]),
        'levels': sorted([l for l in levels if l]),
        'genders': sorted([g for g in genders if g]),
    })
