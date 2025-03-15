from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from main.models import Exercise, Favourite, Workout
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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
            favourites = Favourite.objects.filter(user=request.user, workout_id=id)
        elif type == 'e':
            favourites = Favourite.objects.filter(user=request.user, exercise_id=id)
        else:
            return JsonResponse({'error': 'Invalid type'}, status=400)

        for favourite in favourites:
            favourite.delete()

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
