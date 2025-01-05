from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from main.forms import ExerciseTermSearchForm, ExerciseSearchForm
from main.search.search import almacenar_datos, ej_buscar, ej_buscar_nombre_instrucciones


def index(request):
    return render(request, 'index.html',{'STATIC_URL':settings.STATIC_URL})

def populateDatabase(request):
    mensaje = almacenar_datos()
    return JsonResponse({'mensaje': mensaje})

# Ejercicios

def search_ex(request):
    formulario = ExerciseSearchForm()
    items = None
    name = ""
    exerciseCategory = "Seleccionar"
    muscle = "N/A"
    if request.method == 'POST':
        formulario = ExerciseSearchForm(request.POST)
        
        if formulario.is_valid():
            name = formulario.cleaned_data['name']
            exerciseCategory = formulario.cleaned_data['exerciseCategory']
            if exerciseCategory == "Seleccionar":
                exerciseCategory = ""
            muscle = formulario.cleaned_data['muscle']
            if muscle == "N/A":
                muscle = ""

            items = ej_buscar(name=name, cat=exerciseCategory, muscle=muscle)
            
    datos = {
        'name': name,
        'exerciseCategory': exerciseCategory,
        'muscle': muscle,
    }
    
    return render(request, 'buscar_ejercicios.html', {'formulario':formulario, 'items': items, 'datos': datos, 'STATIC_URL':settings.STATIC_URL})

    

def search_ex_name_instructions(request):
    formulario = ExerciseTermSearchForm()
    items = None
    termino = None
    
    if request.method == 'POST':
        formulario = ExerciseTermSearchForm(request.POST)
        
        if formulario.is_valid():
            termino = formulario.cleaned_data['term']
            items = ej_buscar_nombre_instrucciones(termino)
            for item in items:
                item['exerciseCategory'] = item.get('exerciseCategory', 'N/A').replace(',', ', ')
                priMuscles = item.get('priMuscles', [])
                secMuscles = item.get('secMuscles', [])
                if isinstance(priMuscles, list):
                    priMusclesParsed = ', '.join(priMuscles)
                    item['priMuscles'] = priMusclesParsed
    
                if isinstance(secMuscles, list):
                    secMusclesParsed = ', '.join(secMuscles)
                    if secMusclesParsed == 'N/A':
                        item['secMuscles'].clear()                    
                    else:
                        item['secMuscles'] = secMusclesParsed
    
    return render(request, 'buscar_ejercicios_nombre_instrucciones.html', {'formulario':formulario, 'items': items, 'termino': termino, 'STATIC_URL':settings.STATIC_URL})
