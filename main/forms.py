#encoding:utf-8
from django import forms
from main.models.exercise import Exercise, Muscle
from main.models.workout import Workout
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
    order = forms.ChoiceField(
        label="Orden",
        choices=[],
        initial="name",
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order'].choices = [('name', 'Nombre'), ('likes_count', 'Me gusta')]


 
class ExerciseSearchForm(forms.Form):
    name = forms.CharField(label="Nombre", widget=forms.TextInput, required=False)
    exerciseCategory = forms.ChoiceField(
        label="Categoría",
        choices=[],
        initial="Seleccionar",
        required=False
    )
    muscle = forms.ChoiceField(
        label="Músculo",
        choices=[],
        initial="N/A",
        required=False
    )
    order = forms.ChoiceField(
        label="Orden",
        choices=[],
        initial="likes_count",
        required=False
    )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Consultas a la base de datos para obtener categorías y músculos
        categories = Exercise.objects.values_list('exerciseCategory', flat=True).distinct()
        unique_categories = list(set(chain.from_iterable(cat.split(',') for cat in categories if cat)))
        unique_categories.insert(0, "Seleccionar")

        primary_muscles = Muscle.objects.filter(primary__isnull=False).distinct()
        secondary_muscles = Muscle.objects.filter(secondary__isnull=False).distinct()
        muscles = list((primary_muscles | secondary_muscles).distinct())

        # Actualizar los choices de los campos
        self.fields['exerciseCategory'].choices = [(cat, cat) for cat in unique_categories if cat]
        self.fields['muscle'].choices = [(muscle.name, muscle.name) for muscle in muscles]
        self.fields['order'].choices = [('name', 'Nombre'), ('likes_count', 'Me gusta')]


class WorkoutTermSearchForm(forms.Form):
    term = forms.CharField(label="Término", widget=forms.TextInput, required=False)

    order = forms.ChoiceField(
        label="Orden",
        choices=[],
        initial="name",
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order'].choices = [('name', 'Nombre'), ('popularity', 'Popularidad'), ('likes_count', 'Me gusta'), ('creationDate', 'Fecha de creación')]

 
class WorkoutSearchForm(forms.Form):
    name = forms.CharField(label="Nombre", widget=forms.TextInput, required=False)
    workoutCategory = forms.ChoiceField(
        label="Categoría",
        choices=[],
        initial="Seleccionar",
        required=False
    )
    level = forms.ChoiceField(
        label="Nivel",
        choices=[],
        initial="N/A",
        required=False
    )
    gender = forms.ChoiceField(
        label="Género",
        choices=[],
        initial="N/A",
        required=False
    )
    order = forms.ChoiceField(
        label="Orden",
        choices=[],
        initial="name",
        required=False
    )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Consultas a la base de datos para obtener categorías, niveles y géneros
        categories = Workout.objects.values_list('workoutCategory', flat=True).distinct()
        unique_categories = list(set(chain.from_iterable(cat.split(',') for cat in categories if cat)))
        unique_categories.insert(0, "Seleccionar")

        levels = set(Workout.objects.values_list('level', flat=True).distinct())
        genders = set(Workout.objects.values_list('gender', flat=True).distinct())

        # Actualizar los choices de los campos
        self.fields['workoutCategory'].choices = [(cat, cat) for cat in unique_categories if cat]
        self.fields['level'].choices = [(level, level) for level in levels if level]
        self.fields['gender'].choices = [(gender, gender) for gender in genders if gender]
        self.fields['order'].choices = [('name', 'Nombre'), ('popularity', 'Popularidad'), ('likes_count', 'Me gusta'), ('creationDate', 'Fecha de creación')]
