#encoding:utf-8
from django import forms
from main.models import Exercise, Muscle, Workout
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from itertools import chain

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellido")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class EditUserForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ExerciseTermSearchForm(forms.Form):
    term = forms.CharField(label="Término", widget=forms.TextInput, required=False)

 
class ExerciseSearchForm(forms.Form):
    categories = Exercise.objects.values_list('exerciseCategory', flat=True).distinct()

    unique_categories = list(set(chain.from_iterable(cat.split(',') for cat in categories if cat)))
    
    unique_categories.insert(0, "Seleccionar")
        
    primary_muscles = Muscle.objects.filter(primary__isnull=False).distinct()

    secondary_muscles = Muscle.objects.filter(secondary__isnull=False).distinct()

    muscles = list((primary_muscles | secondary_muscles).distinct())

    name = forms.CharField(label="Nombre", widget=forms.TextInput, required=False)
    exerciseCategory = forms.ChoiceField(
        label="Categoría", 
        choices=[(cat, cat) for cat in unique_categories if cat], 
        initial="Seleccionar",
        required=False
    )
    muscle = forms.ChoiceField(
        label="Músculo", 
        choices=[(muscle.name, muscle.name) for muscle in muscles],
        initial="N/A",
        required=False
    )


class WorkoutTermSearchForm(forms.Form):
    term = forms.CharField(label="Término", widget=forms.TextInput, required=False)

 
class WorkoutSearchForm(forms.Form):
    categories = Workout.objects.values_list('workoutCategory', flat=True).distinct()

    unique_categories = list(set(chain.from_iterable(cat.split(',') for cat in categories if cat)))
    
    unique_categories.insert(0, "Seleccionar")
        
    levels = set(Workout.objects.values_list('level', flat=True).distinct())

    genders = set(Workout.objects.values_list('gender', flat=True).distinct())

    name = forms.CharField(label="Nombre", widget=forms.TextInput, required=False)
    
    workoutCategory = forms.ChoiceField(
        label="Categoría", 
        choices=[(cat, cat) for cat in unique_categories if cat], 
        initial="Seleccionar",
        required=False
    )
    level = forms.ChoiceField(
        label="Nivel", 
        choices=[(level, level) for level in levels],
        initial="N/A",
        required=False
    )
    gender = forms.ChoiceField(
        label="Género", 
        choices=[(gender, gender) for gender in genders],
        initial="N/A",
        required=False
    )
