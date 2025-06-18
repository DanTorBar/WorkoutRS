from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from main.importers.manager import import_health_data, IMPORTERS, preparse_health_data
from .serializers import ImportHealthDataSerializer

class GenericImportAPIView(APIView):
    """
    Endpoint para importar datos de salud desde un ZIP enviado por el cliente.
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = ImportHealthDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        zip_file = serializer.validated_data['file']
        source   = serializer.validated_data['source']

        try:
            parsed = import_health_data(request.user, zip_file, source)
            return Response(parsed, status=status.HTTP_200_OK)
        except ValueError as e:
            # Si tu import_health_data lanza errores de validación
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PreImportAPIView(APIView):
    """
    Recibe un ZIP y un source, parsea y devuelve los datos extraídos.
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = ImportHealthDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        zip_file = serializer.validated_data['file']
        source   = serializer.validated_data['source']

        try:
            parsed = preparse_health_data(zip_file, source)
            return Response(parsed, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
