from django.shortcuts import render
from django.conf import settings
from main.search.search import almacenar_datos


def index(request):
    return render(request, 'index.html',{'STATIC_URL':settings.STATIC_URL})

def populateDatabase(request):
    almacenar_datos()
    return render(request, 'index.html')
