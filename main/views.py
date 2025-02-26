from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.urls import reverse
from main.forms import CustomUserCreationForm, EditUserForm, ExerciseTermSearchForm, ExerciseSearchForm, WorkoutTermSearchForm, WorkoutSearchForm
from main.models import Exercise, Favourite, Muscle, Workout
from main.search.search import almacenar_datos, ej_buscar, ej_buscar_nombre_instrucciones, ru_buscar, ru_buscar_nombre_descripcion
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from main.recommendations.recommendations import calcular_similitud


def index(request):
    return render(request, 'index.html',{'STATIC_URL':settings.STATIC_URL})

def populateDatabase(request):
    mensaje = almacenar_datos()
    return JsonResponse({'mensaje': mensaje})

# Usuarios

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse('inicio'))
        else:
            print(form.errors)  # Esto mostrará los errores en la consola

    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


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


# Ejercicios

def search_ex(request):
    formulario = ExerciseSearchForm()
    ejercicios = None
    name = ""
    exerciseCategory = "Seleccionar"
    muscle = "N/A"
    esPost = False
    if request.method == 'POST':
        formulario = ExerciseSearchForm(request.POST)
        esPost = True

        if formulario.is_valid():
            name = formulario.cleaned_data['name']
            exerciseCategory = formulario.cleaned_data['exerciseCategory']
            if exerciseCategory == "Seleccionar":
                exerciseCategory = ""
            muscle = formulario.cleaned_data['muscle']
            if muscle == "N/A":
                muscle = ""

            ejercicios = ej_buscar(name=name, cat=exerciseCategory, muscle=muscle, user=request.user)

    datos = {
        'name': name,
        'exerciseCategory': exerciseCategory,
        'muscle': muscle,
    }
    
    return render(request, 'buscar_ejercicios.html', {'formulario':formulario, 'ejercicios': ejercicios, 'datos': datos, 'esPost': esPost,'STATIC_URL':settings.STATIC_URL})

    

def search_ex_name_instructions(request):
    formulario = ExerciseTermSearchForm()
    ejercicios = None
    termino = None
    
    if request.method == 'POST':
        formulario = ExerciseTermSearchForm(request.POST)
        
        if formulario.is_valid():
            termino = formulario.cleaned_data['term']
            ejercicios = ej_buscar_nombre_instrucciones(termino, user=request.user)
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
    
    return render(request, 'buscar_ejercicios_nombre_instrucciones.html', {'formulario':formulario, 'ejercicios': ejercicios, 'termino': termino, 'STATIC_URL':settings.STATIC_URL})

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
# Rutinas

def search_wt(request):
    formulario = WorkoutSearchForm()
    rutinas = None
    esPost = False
    name = ""
    workoutCategory = "Seleccionar"
    level = "N/A"
    gender = "N/A"

    if request.method == 'POST':
        esPost = True
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

            rutinas = ru_buscar(name=name, cat=workoutCategory, level=level, gender=gender, user=request.user)
            
    datos = {
        'name': name,
        'workoutCategory': workoutCategory,
        'level': level,
        'gender': gender
    }
    
    return render(request, 'buscar_rutinas.html', {'formulario':formulario, 'rutinas': rutinas, 'datos': datos, 'esPost':esPost, 'STATIC_URL':settings.STATIC_URL})
    

def search_wt_name_description(request):
    formulario = WorkoutTermSearchForm()
    rutinas = None
    termino = None
    
    if request.method == 'POST':
        formulario = WorkoutTermSearchForm(request.POST)
        
        if formulario.is_valid():
            termino = formulario.cleaned_data['term']
            rutinas = ru_buscar_nombre_descripcion(termino, user=request.user)

    
    return render(request, 'buscar_rutinas_nombre_descripcion.html', {'formulario':formulario, 'rutinas': rutinas, 'termino': termino, 'STATIC_URL':settings.STATIC_URL})

def workout_detail(request, id):
    rutina = get_object_or_404(Workout, id=id)
    
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
    rutinasRec = []
    
    if rutina:
        rutinasRec = recommend_workouts(id)
        for rutina in rutinasRec:
            rutina['idWorkout'] = rutina.get('id')

        
    context = {
        'rutina': rutina,
        'rutinas': rutinasRec,
        'days': days,
        'STATIC_URL': settings.STATIC_URL,
    }
    
    return render(request, 'rutina.html', context)


# Favoritos

@login_required
def add_favourite(request, type, id):
    if request.method == 'POST':
        if type == 'w':
            item = get_object_or_404(Workout, id=id)
            Favourite.objects.get_or_create(user=request.user, workout=item)
        elif type == 'e':
            item = get_object_or_404(Exercise, id=id)
            Favourite.objects.get_or_create(user=request.user, exercise=item)
        return JsonResponse({'status': 'added'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def delete_favourite(request, type, id):
    if request.method == 'POST':
        if type == 'w':
            Favourite.objects.filter(user=request.user, workout_id=id).delete()
        elif type == 'e':
            Favourite.objects.filter(user=request.user, exercise_id=id).delete()
        return JsonResponse({'status': 'deleted'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def list_favourites(request):
    favourites = Favourite.objects.filter(user=request.user)

    # Convertir rutinas y ejercicios en diccionarios limpios
    rutinas = [
        {
            'idWorkout': fav.workout.id,
            'workoutName': fav.workout.workoutName,
            'workoutCategory': fav.workout.workoutCategory,
            'level': fav.workout.level,
            'gender': fav.workout.gender,
            'bodyPart': fav.workout.bodyPart,
            'description': fav.workout.description,
            'is_favourite': True,
        }
        for fav in favourites if fav.workout is not None
    ]

    ejercicios = [
        {
            'idExercise': fav.exercise.id,
            'exerciseName': fav.exercise.exerciseName,
            'exerciseCategory': fav.exercise.exerciseCategory,
            'instructions': fav.exercise.instructions,
            'is_favourite': True,
        }
        for fav in favourites if fav.exercise is not None
    ]

    return render(request, 'favoritos.html', {'favourites': favourites, 'rutinas': rutinas, 'ejercicios': ejercicios})


# Recomendaciones

def recommend_workouts(id):
    # Obtener todas las rutinas
    rutinas = list(Workout.objects.all().values(
        "id", "workoutName", "workoutCategory", "level", "gender", "bodyPart", "description"
    ))

    # Obtener las recomendaciones
    recomendaciones = calcular_similitud(rutinas, id, ["workoutName", "workoutCategory", "level", "gender", "bodyPart"], 5)

    return recomendaciones

def recommend_exercises(id):
    # Obtener todos los ejercicios
    ejercicios = list(Exercise.objects.all().values(
        "id", "exerciseName", "exerciseCategory", "priMuscles", "secMuscles"
    ))

    # Obtener las recomendaciones
    recomendaciones = calcular_similitud(ejercicios, id, ["exerciseName", "exerciseCategory", "exerciseCategory", "priMuscles", "secMuscles"], 5)

    return recomendaciones