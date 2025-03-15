from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from main.search.search import almacenar_datos
from django.shortcuts import render


def index(request):
    return render(request, 'index.html',{'STATIC_URL':settings.STATIC_URL})

def populateDatabase(request):
    mensaje = almacenar_datos()
    return JsonResponse({'mensaje': mensaje})
