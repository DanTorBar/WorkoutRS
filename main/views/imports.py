from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from importers.manager import import_health_data

@method_decorator(csrf_exempt, name='dispatch')
class GenericImportView(View):
    def post(self, request):
        zip_file = request.FILES.get('file')
        source = request.POST.get('source')  # Puede ser 'garmin', 'fitbit', etc.

        if not zip_file:
            return JsonResponse({'error': 'No file provided'}, status=400)

        if not source:
            return JsonResponse({'error': 'No source specified'}, status=400)

        try:
            parsed = import_health_data(request.user, zip_file, source)
            return JsonResponse(parsed)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
