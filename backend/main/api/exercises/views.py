# main/api/exercises/views.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from main.models.exercise import Exercise
from main.search.search import buscar_ejercicios_por_nombre_instrucciones, ej_buscar
from main.api.workoutRS.views import recommend_exercises
from .serializers import ExerciseSerializer


class ExerciseViewSet(viewsets.ModelViewSet):
    """
    ViewSet que expone:
      - list/retrieve/create/update/destroy de ejercicios
      - GET /search/ → formulario libre
      - GET /search-name-instructions/ → búsqueda por término
      - retrieve() añade campo 'recommendations'
    """
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Búsqueda tipo search_ex:
          ?name=&exerciseCategory=&muscle=&order=
        """
        name = request.query_params.get('name', '')
        cat  = request.query_params.get('exerciseCategory', '')
        muscle = request.query_params.get('muscle', '')
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
            order=order
        )

        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)

        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)

    @action(detail=False, methods=['get'], url_path='search-name-instructions')
    def search_name_instructions(self, request):
        """
        Búsqueda tipo search_ex_name_instructions:
          ?term=&order=
        """
        term  = request.query_params.get('term', '')
        order = request.query_params.get('order', 'name')

        results = buscar_ejercicios_por_nombre_instrucciones(
            termino=term,
            user=request.user,
            order=order
        )
        # Buscar instancias por ID para serializar
        ids = [int(item.get('id')) for item in results]
        qs  = Exercise.objects.filter(id__in=ids).order_by(order)

        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)

    def retrieve(self, request, *args, **kwargs):
        """
        retrieve + recomendaciones:
        GET /api/v1/exercises/{pk}/
        """
        instance = self.get_object()
        ser = self.get_serializer(instance)

        # calcular recomendaciones (lista de dicts con al menos 'idExercise' o 'id')
        recs = recommend_exercises(instance.id)
        # convertir a instancias para usar el serializer
        rec_ids = [r.get('idExercise') or r.get('id') for r in recs]
        rec_qs  = Exercise.objects.filter(id__in=rec_ids)
        rec_ser = self.get_serializer(rec_qs, many=True)

        data = ser.data
        data['recommendations'] = rec_ser.data
        return Response(data)
