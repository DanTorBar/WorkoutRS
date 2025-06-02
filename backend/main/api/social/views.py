from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from main.models.social import Comment, Favourite
from .serializers import CommentSerializer, FavouriteSerializer

class FavouriteViewSet(viewsets.ModelViewSet):
    """
    list:   GET  /api/v1/social/favourites/
    create: POST /api/v1/social/favourites/   { "workout": 3 }  o  { "exercise": 5 }
    destroy: DELETE /api/v1/social/favourites/{pk}/
    """
    serializer_class = FavouriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Solo favoritos del usuario actual
        return Favourite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # user se asigna en el serializer.create()
        serializer.save()

    def list(self, request, *args, **kwargs):
        """
        Devuelve la lista de favoritos del usuario actual con información adicional.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Agrega información adicional para el frontend
        data = serializer.data
        for item in data:
            item['liked'] = True  # Marca todos los ítems como 'liked' ya que están en favoritos

        return Response(data)

    @action(detail=False, methods=['delete'], url_path='delete-by-type')
    def delete_by_type(self, request):
        """
        Borra el favorito basado en el tipo y el id del item usando el serializador.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = serializer.delete(serializer.validated_data)
            return Response(result, status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class CommentViewSet(viewsets.ModelViewSet):
    """
    API para ver, crear y reportar comentarios de rutinas o ejercicios.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        workout_id = self.request.query_params.get('workout')
        exercise_id = self.request.query_params.get('exercise')
        qs = Comment.objects.all()
        if workout_id:
            qs = qs.filter(workout_id=workout_id)
        if exercise_id:
            qs = qs.filter(exercise_id=exercise_id)
        return qs.order_by('-date_added')

    def perform_create(self, serializer):
        # No pasar user aquí, el serializer ya lo toma del contexto
        serializer.save()

    # Endpoint para reportar (marcar) un comentario
    def partial_update(self, request, *args, **kwargs):
        # Marcar el comentario como reportado
        instance = self.get_object()
        instance.reported = True
        instance.save(update_fields=["reported"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
