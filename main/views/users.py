from django.shortcuts import render
from django.urls import reverse
from main.forms import CustomUserCreationForm, EditUserForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from main.tasks import revoke_health_data
from rest_framework import generics, permissions
from main.serializers import RegisterSerializer
from rest_framework.parsers import MultiPartParser
from importers.manager import IMPORTERS  # tu dict { 'garmin': GarminImporter, ... }


# Usuarios

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class HealthDataPreImportView(APIView):
    """
    Recibe un ZIP de exportación (Garmin, Fitbit...) y devuelve los campos
    que podemos rellenar del HealthProfile.
    """
    parser_classes = [MultiPartParser]
    permission_classes = []  # AllowAny, no necesita login

    def post(self, request, service_key):
        zip_file = request.FILES.get('file')
        if not zip_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        cls = IMPORTERS.get(service_key.lower())
        if not cls:
            return Response({'error': f'Unknown service {service_key}'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            parsed = cls(zip_file).parse()
            # parsed será un dict con keys: first_name, height, imported_neat_min, etc.
            return Response(parsed)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('inicio')
        else:
            return render(request, 'login.html', {'error': 'Invalid login'})
    return render(request, 'login.html')


@login_required
def user_profile(request):
    return render(request, 'perfil.html', {'user': request.user})


@login_required
def edit_user(request):
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('perfil')
    else:
        form = EditUserForm(instance=request.user)
    
    return render(request, 'editar_usuario.html', {'form': form})


class RevokeHealthDataConsentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Validar que existía consentimiento
        consent = request.user.health_data_consent
        if not consent or not consent.given:
            return Response({"detail": "No hay consentimiento activo."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Disparamos la tarea asíncrona
        revoke_health_data.delay(request.user.id)

        return Response(
            {"detail": "Solicitud de revocación recibida. Borrado en proceso."},
            status=status.HTTP_202_ACCEPTED
        )
