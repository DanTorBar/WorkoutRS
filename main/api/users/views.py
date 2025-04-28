from django.contrib.auth import logout, get_user_model
from rest_framework import viewsets
from rest_framework import status, generics
from rest_framework.views import APIView
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

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RegisterAPIView(generics.CreateAPIView):
    """
    Registra un nuevo usuario.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginAPIView(ObtainAuthToken):
    """
    Login que devuelve token de DRF.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            
            # Usa el serializer de ObtainAuthToken para validar credenciales
            serializer = self.serializer_class(data=request.data,
                                            context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            print(user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.id},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutAPIView(APIView):
    """
    Logout: borra el token de la sesión actual.
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
    GET/PUT/PATCH de los datos del usuario autenticado.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class HealthDataPreImportAPIView(APIView):
    """
    Recibe ZIP de exportación y devuelve campos rellenables del perfil.
    """
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]

    def post(self, request, service_key, *args, **kwargs):
        zip_file = request.FILES.get('file')
        if not zip_file:
            return Response({'error': 'No file provided'},
                            status=status.HTTP_400_BAD_REQUEST)

        cls = IMPORTERS.get(service_key.lower())
        if not cls:
            return Response({'error': f'Unknown service {service_key}'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            parsed = cls(zip_file).parse()
            return Response(parsed, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RevokeHealthDataConsentAPIView(APIView):
    """
    Solicita la revocación de consentimiento y dispara tarea async.
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
