# main/api/exercises/views.py

from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny

from main.models.exercise import Exercise, Muscle
from main.models.logs import ViewLog
from main.search.search import buscar_ejercicios_por_nombre_instrucciones, ej_buscar
from main.api.core.views import recommend_exercises
from .serializers import ExerciseSerializer
from django.contrib.contenttypes.models import ContentType


class ExercisePagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class ExerciseViewSet(viewsets.ModelViewSet):
    """
    ViewSet que expone:
      - list/retrieve/create/update/destroy de ejercicios
      - GET /exercises/?... → formulario libre
      - retrieve() añade campo 'recommendations'
    """
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    pagination_class = ExercisePagination

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        """
        Búsqueda tipo search_ex:
          ?name=&exerciseCategory=&muscle=&order=
        """
        name = request.query_params.get('name', '')
        cat  = request.query_params.get('exerciseCategory', '')
        muscle = request.query_params.get('muscle', '')
        equipment  = request.query_params.get('equipment', '')
        order  = request.query_params.get('order', 'name')

        if cat == 'Seleccionar':
            cat = ''
        if muscle == 'N/A':
            muscle = ''

        qs = ej_buscar(
            name=name,
            cat=cat,
            muscle=muscle,
            user=request.user,
            equipment=equipment,
            order=order
        )

        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)

        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)

    def retrieve(self, request, *args, **kwargs):
        """
        retrieve + recomendaciones:
        GET /api/v1/exercises/{pk}/
        """
        instance = self.get_object()
        ser = self.get_serializer(instance)
        
        # registrar la vista
        ViewLog.objects.create(
            user = request.user,
            content_type = ContentType.objects.get_for_model(instance),
            object_id = instance.pk
        )

        # calcular recomendaciones (lista de dicts con al menos 'idExercise' o 'id')
        recs = recommend_exercises(instance.id)
        # convertir a instancias para usar el serializer
        rec_ids = [r.get('idExercise') or r.get('id') for r in recs]
        rec_qs  = Exercise.objects.filter(id__in=rec_ids)
        rec_ser = self.get_serializer(rec_qs, many=True)

        data = ser.data
        data['recommendations'] = rec_ser.data
        return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def exercise_options(request):
    # Granularizar categories
    raw_categories = Exercise.objects.values_list('exerciseCategory', flat=True).distinct()
    categories_set = set()
    for c in raw_categories:
        if c:
            categories_set.update([x.strip() for x in c.split(',') if x.strip()])
    
    # Granularizar equipment
    raw_equipment = Exercise.objects.values_list('equipment', flat=True).distinct()
    equipment_set = set()
    for e in raw_equipment:
        if e:
            equipment_set.update([x.strip() for x in e.split(',') if x.strip()])

    print(categories_set)
    print(equipment_set)

    # Get all unique muscle names from both priMuscles and secMuscles
    pri = Muscle.objects.filter(primary__isnull=False).values_list('name', flat=True).distinct()
    sec = Muscle.objects.filter(secondary__isnull=False).values_list('name', flat=True).distinct()
    muscles = set(list(pri) + list(sec))
    return Response({
        'categories': sorted(categories_set),
        'equipment': sorted(equipment_set),
        'muscles': sorted([m for m in muscles if m]),
    })
