from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from main.forms import ExerciseTermSearchForm, ExerciseSearchForm, WorkoutTermSearchForm, WorkoutSearchForm
from main.models import Exercise, Workout
from main.search.search import almacenar_datos, ej_buscar, ej_buscar_nombre_instrucciones, ru_buscar, ru_buscar_nombre_descripcion


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

def exercise_detail(request, id):
    # Obtener el ejercicio correspondiente al id
    ejercicio = get_object_or_404(Exercise, idExercise=id)
    
    context = {
        'ejercicio': ejercicio,
        'STATIC_URL': settings.STATIC_URL,
    }
    
    return render(request, 'ejercicio.html', context)
# Rutinas

def search_wt(request):
    formulario = WorkoutSearchForm()
    items = None
    name = ""
    workoutCategory = "Seleccionar"
    level = "N/A"
    gender = "N/A"

    if request.method == 'POST':
        formulario = WorkoutSearchForm(request.POST)
        
        if formulario.is_valid():
            name = formulario.cleaned_data['name']
            workoutCategory = formulario.cleaned_data['workoutCategory']
            if workoutCategory == "Seleccionar":
                workoutCategory = ""
            level = formulario.cleaned_data['level']
            if level == "N/A":
                level = ""
                
            gender = formulario.cleaned_data['gender']
            if gender == "N/A":
                gender = ""

            items = ru_buscar(name=name, cat=workoutCategory, level=level, gender=gender)
            
            for i in items:
                i['link'] = i.get('workoutName', 'N/A').replace(' ', '_').lower()
            
    datos = {
        'name': name,
        'workoutCategory': workoutCategory,
        'level': level,
        'gender': gender
    }
    
    return render(request, 'buscar_rutinas.html', {'formulario':formulario, 'items': items, 'datos': datos, 'STATIC_URL':settings.STATIC_URL})

    

def search_wt_name_description(request):
    formulario = WorkoutTermSearchForm()
    items = None
    termino = None
    
    if request.method == 'POST':
        formulario = WorkoutTermSearchForm(request.POST)
        
        if formulario.is_valid():
            termino = formulario.cleaned_data['term']
            items = ru_buscar_nombre_descripcion(termino)
            for i in items:
                i['link'] = i.get('workoutName', 'N/A').replace(' ', '_').lower()

    
    return render(request, 'buscar_rutinas_nombre_descripcion.html', {'formulario':formulario, 'items': items, 'termino': termino, 'STATIC_URL':settings.STATIC_URL})

def workout_detail(request, link):
    rutina = get_object_or_404(Workout, workoutName=link.replace('_', ' ').upper())
    
    # Preparar los datos de los días de la rutina
    days = [
        rutina.day1.all(),
        rutina.day2.all(),
        rutina.day3.all(),
        rutina.day4.all(),
        rutina.day5.all(),
        rutina.day6.all(),
        rutina.day7.all(),
    ]
        
    context = {
        'rutina': rutina,
        'days': days,
        'STATIC_URL': settings.STATIC_URL,
    }
    
    return render(request, 'rutina.html', context)