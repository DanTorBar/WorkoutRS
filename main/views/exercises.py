from django.shortcuts import get_object_or_404, render
from django.conf import settings
from main.forms import ExerciseTermSearchForm, ExerciseSearchForm
from main.models import Exercise, Muscle
from main.search.search import buscar_ejercicios_por_nombre_instrucciones, ej_buscar
from django.shortcuts import render
from main.views.recommendations import recommend_exercises

# Ejercicios

def search_ex(request):
    formulario = ExerciseSearchForm()
    ejercicios = None
    name = ""
    exerciseCategory = "Seleccionar"
    muscle = "N/A"
    esPost = False
    order = 'name'
    
    if request.method == 'POST':
        formulario = ExerciseSearchForm(request.POST)
        esPost = True

        if formulario.is_valid():
            name = formulario.cleaned_data['name']
            exerciseCategory = formulario.cleaned_data['exerciseCategory']
            order = formulario.cleaned_data['order']
            if exerciseCategory == "Seleccionar":
                exerciseCategory = ""
            muscle = formulario.cleaned_data['muscle']
            if muscle == "N/A":
                muscle = ""

            ejercicios = ej_buscar(name=name, cat=exerciseCategory, muscle=muscle, user=request.user, order=order)

    datos = {
        'name': name,
        'exerciseCategory': exerciseCategory,
        'muscle': muscle,
        'order': order,
    }
    
    return render(request, 'buscar_ejercicios.html', {'formulario':formulario, 'ejercicios': ejercicios, 'datos': datos, 'esPost': esPost,'STATIC_URL':settings.STATIC_URL})

    

def search_ex_name_instructions(request):
    formulario = ExerciseTermSearchForm()
    ejercicios = None
    termino = None
    order = 'name'
    
    if request.method == 'POST':
        formulario = ExerciseTermSearchForm(request.POST)
        
        if formulario.is_valid():
            termino = formulario.cleaned_data['term']
            order = formulario.cleaned_data['order']
            ejercicios = buscar_ejercicios_por_nombre_instrucciones(termino, user=request.user, order=order)
            for item in ejercicios:
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
    
    return render(request, 'buscar_ejercicios_nombre_instrucciones.html', {'formulario':formulario, 'ejercicios': ejercicios, 'termino': termino, 'order': order, 'STATIC_URL':settings.STATIC_URL})

def exercise_detail(request, id):
    # Obtener el ejercicio correspondiente al id
    ejercicio = get_object_or_404(Exercise, id=id)
    
    ejerciciosRec = []
    
    if ejercicio:
        ejerciciosRec = recommend_exercises(id)
        for ej in ejerciciosRec:
            ej['priMuscles'] = Muscle.objects.get(id=int(ej.get('priMuscles')))
            ej['secMuscles'] = Muscle.objects.get(id=int(ej.get('secMuscles')))
            ej['idExercise'] = ej.get('id')

    
    context = {
        'ejercicio': ejercicio,
        'ejercicios': ejerciciosRec,
        'STATIC_URL': settings.STATIC_URL,
    }
    
    return render(request, 'ejercicio.html', context)
