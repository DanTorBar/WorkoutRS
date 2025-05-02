# main/api/users/views.py

from django.contrib.auth import get_user_model, logout
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from importers.manager import IMPORTERS
from main.tasks import revoke_health_data
from .serializers import (
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterAPIView(generics.CreateAPIView):
    """
    POST /api/v1/users/register/
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginAPIView(ObtainAuthToken):
    """
    POST /api/v1/users/login/  → { username, password }
    devuelve { token, user_id }
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.id})


class LogoutAPIView(APIView):
    """
    POST /api/v1/users/logout/
    Borra el token y cierra sesión.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Asumiendo TokenAuthentication
        if request.auth:
            request.auth.delete()
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserAPIView(generics.RetrieveUpdateAPIView):
    """
    GET, PUT, PATCH /api/v1/users/me/
    Devuelve y actualiza datos del usuario autenticado.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class HealthDataPreImportAPIView(APIView):
    """
    POST /api/v1/users/<service_key>/preimport/
    Recibe multipart/form-data { file } y devuelve preview de datos.
    """
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]

    def post(self, request, service_key, *args, **kwargs):
        zip_file = request.FILES.get('file')
        if not zip_file:
            return Response({'error': 'No file provided'},
                            status=status.HTTP_400_BAD_REQUEST)

        importer_cls = IMPORTERS.get(service_key.lower())
        if not importer_cls:
            return Response({'error': f'Unknown service {service_key}'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            parsed = importer_cls(zip_file).parse()
            return Response(parsed, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RevokeHealthDataConsentAPIView(APIView):
    """
    POST /api/v1/users/revoke-consent/
    Lanza la tarea asíncrona de borrado de datos de salud.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        consent = getattr(request.user, 'health_data_consent', None)
        if not consent or not consent.given:
            return Response({"detail": "No active consent."},
                            status=status.HTTP_400_BAD_REQUEST)

        revoke_health_data.delay(request.user.id)
        return Response(
            {"detail": "Revocation requested; deletion in progress."},
            status=status.HTTP_202_ACCEPTED
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD de usuarios. Solo accesible para admin (ajusta permisos si lo deseas).
    Además expone una ruta extra:
    GET /api/v1/users/me/  → datos del usuario autenticado
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """ Alias de CurrentUserAPIView """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
