from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status

from main.models.social import Favourite
from .serializers import FavouriteSerializer

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

    def destroy(self, request, *args, **kwargs):
        """
        Borra el favorito y devuelve status.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)