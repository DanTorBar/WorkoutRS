from django.shortcuts import get_object_or_404, render
from django.conf import settings
from main.forms import WorkoutTermSearchForm, WorkoutSearchForm
from main.models import Workout, WorkoutExercise
from main.search.search import buscar_rutinas_por_nombre_descripcion, ru_buscar
from django.shortcuts import render
from main.views.recommendations import recommend_workouts
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Count, Q


# Rutinas

def search_wt(request):
    formulario = WorkoutSearchForm()
    rutinas = None
    esPost = False
    name = ""
    workoutCategory = "Seleccionar"
    level = "N/A"
    gender = "N/A"
    order = 'name'

    if request.method == 'POST':
        esPost = True
        formulario = WorkoutSearchForm(request.POST)
        
        if formulario.is_valid():
            name = formulario.cleaned_data['name']
            workoutCategory = formulario.cleaned_data['workoutCategory']
            order = formulario.cleaned_data['order']
            if workoutCategory == "Seleccionar":
                workoutCategory = ""
            level = formulario.cleaned_data['level']
            if level == "N/A":
                level = ""
                
            gender = formulario.cleaned_data['gender']
            if gender == "N/A":
                gender = ""

            rutinas = ru_buscar(name=name, cat=workoutCategory, level=level, gender=gender, user=request.user, order=order)
            
    datos = {
        'name': name,
        'workoutCategory': workoutCategory,
        'level': level,
        'gender': gender,
        'order': order,
    }
    
    return render(request, 'buscar_rutinas.html', {'formulario':formulario, 'rutinas': rutinas, 'datos': datos, 'esPost':esPost, 'STATIC_URL':settings.STATIC_URL})
    

def search_wt_name_description(request):
    formulario = WorkoutTermSearchForm()
    rutinas = None
    termino = None
    order = 'name'
    
    if request.method == 'POST':
        formulario = WorkoutTermSearchForm(request.POST)
        
        if formulario.is_valid():
            termino = formulario.cleaned_data['term']
            order = formulario.cleaned_data['order']
            rutinas = buscar_rutinas_por_nombre_descripcion(termino, user=request.user, order=order)

    
    return render(request, 'buscar_rutinas_nombre_descripcion.html', {'formulario':formulario, 'rutinas': rutinas, 'termino': termino, 'order': order, 'STATIC_URL':settings.STATIC_URL})

def workout_detail(request, id):
    rutina = get_object_or_404(Workout, id=id)
    
    # Preparar los datos de los días de la rutina
    days = []
    for day in range(1, 8):  # Días de la semana (1 a 7)
        exercises = WorkoutExercise.objects.filter(workout=rutina, day=day).select_related('exercise')
        days.append([we.exercise for we in exercises])
    
    rutinasRec = []
    
    if rutina:
        rutinasRec = recommend_workouts(id)
        for ru in rutinasRec:
            ru['idWorkout'] = ru.get('id')

    context = {
        'rutina': rutina,
        'rutinas': rutinasRec,
        'days': days,
        'STATIC_URL': settings.STATIC_URL,
    }
    
    return render(request, 'rutina.html', context)

def order_results(results, order):
    if order == 'name':
        results = sorted(results, key=lambda x: x.workoutName.lower())
    elif order == 'popularity':
        recent_period = now() - timedelta(days=14)  # Últimas dos semanas
        for workout in results:
            recent_likes = workout.favourite_set.filter(date_added__gte=recent_period).count()
            workout.recent_likes = recent_likes
        results = sorted(results, key=lambda x: getattr(x, 'recent_likes', 0), reverse=True)
    elif order == 'likes_count':
        results = sorted(results, key=lambda x: x.likes_count, reverse=True)
    elif order == 'creationDate':
        results = sorted(results, key=lambda x: x.creationDate, reverse=True)
    return results