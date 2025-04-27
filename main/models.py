from django.db import models
from django.contrib.auth.models import User
from main.constants import ACTIVITY_LEVEL_CHOICES

# Exercise related models
class Muscle(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Exercise(models.Model):
    exerciseName = models.TextField(verbose_name='Exercise name')
    exerciseCategory = models.CharField(max_length=200, verbose_name='Exercise Category', null=True)
    priMuscles = models.ManyToManyField(Muscle, related_name='primary', verbose_name='Primary Muscles')
    secMuscles = models.ManyToManyField(Muscle, related_name='secondary', verbose_name='Secondary Muscles')
    video = models.URLField(verbose_name='Video', null=True)
    instructions = models.TextField(verbose_name='Instructions', null=True)
    equipment = models.CharField(max_length=200, verbose_name='Equipment', null=True)
    likes_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.exerciseName

    class Meta:
        ordering = ('exerciseName', )

class Workout(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    workoutName = models.TextField(verbose_name="Workout name")
    workoutCategory = models.CharField(max_length=200, verbose_name="Workout Category", null=True)
    level = models.CharField(max_length=30, verbose_name="Level", null=True)
    gender = models.CharField(max_length=30, verbose_name="Gender", null=True)
    bodyPart = models.CharField(max_length=100, verbose_name="Body Part", null=True)
    description = models.TextField(verbose_name="Description", null=True, blank=True)
    likes_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.workoutName

    class Meta:
        ordering = ['workoutName']


class WorkoutExercise(models.Model):
    
    DAYS_OF_WEEK = [
        (1, "Lunes"),
        (2, "Martes"),
        (3, "Miércoles"),
        (4, "Jueves"),
        (5, "Viernes"),
        (6, "Sábado"),
        (7, "Domingo"),
    ]

    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS_OF_WEEK)

    def __str__(self):
        return f"{self.workout.workoutName} - {self.exercise.exerciseName}"

    class Meta:
        unique_together = ('workout', 'exercise', 'day')

# User related models
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class HealthProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # --- Datos personales ---
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=[
        ('masculino', 'MASCULINO'),
        ('femenino', 'FEMENINO'),
        ('otro', 'OTRO'),
        ('desconocido', 'DESCONOCIDO'),
    ], default='unknown')

    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # --- Objetivos y condiciones ---
    goals         = models.ManyToManyField('Goal', blank=True, verbose_name=_("Objetivos"))
    conditions    = models.ManyToManyField('Condition', blank=True, verbose_name=_("Condiciones"))

    # --- Entornos y equipamiento disponible ---
    equipment     = models.ManyToManyField('Equipment', blank=True, verbose_name=_("Equipamiento"))
    environment   = models.CharField(_("Entorno"), max_length=200, blank=True)

    # --- Datos importados (minutos semanales) ---
    imported_neat_min = models.PositiveIntegerField(null=True, blank=True, help_text="Actividad general (NEAT)")
    imported_cardio_mod_min = models.PositiveIntegerField(null=True, blank=True, help_text="Cardio moderado")
    imported_cardio_vig_min = models.PositiveIntegerField(null=True, blank=True, help_text="Cardio vigoroso")

    # --- Fallback manual (niveles 0–5) ---
    neat_level = models.PositiveSmallIntegerField(choices=ACTIVITY_LEVEL_CHOICES, default=0)
    cardio_mod_level = models.PositiveSmallIntegerField(choices=ACTIVITY_LEVEL_CHOICES, default=0)
    cardio_vig_level = models.PositiveSmallIntegerField(choices=ACTIVITY_LEVEL_CHOICES, default=0)
    strength_level = models.PositiveSmallIntegerField(choices=ACTIVITY_LEVEL_CHOICES, default=0)

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"HealthProfile of {self.user.username}"

class Goal(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Condition(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Equipment(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class HealthDataConsent(models.Model):
    """
    Guarda el consentimiento explícito del usuario al tratamiento de sus datos de salud.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="health_data_consent"
    )
    given = models.BooleanField(
        default=False,
        help_text="¿Ha dado el usuario consentimiento para procesar sus datos de salud?"
    )
    given_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Cuándo dio el usuario su consentimiento"
    )

    def __str__(self):
        return f"{self.user.username}: consent={self.given}"

from django.conf import settings
from django.db import models

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('IMPORT',  'Importación de datos'),
        ('DELETE',  'Borrado de datos'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    detail = models.TextField(blank=True, help_text="Detalles adicionales en JSON o texto.")

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} {self.action} at {self.timestamp}"


#Social related models
class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourite')
    workout = models.ForeignKey('Workout', on_delete=models.CASCADE, null=True, blank=True)
    exercise = models.ForeignKey('Exercise', on_delete=models.CASCADE, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.workout:
            return f"Favorito: {self.user.username} - Rutina: {self.workout.workoutName}"
        elif self.exercise:
            return f"Favorito: {self.user.username} - Ejercicio: {self.exercise.exerciseName}"
        return "Favorito sin asociación"

    class Meta:
        unique_together = ('user', 'workout', 'exercise')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.workout:
            self.workout.likes_count = Favourite.objects.filter(workout=self.workout).count()
            self.workout.save()
        elif self.exercise:
            self.exercise.likes_count = Favourite.objects.filter(exercise=self.exercise).count()
            self.exercise.save()

    def delete(self, *args, **kwargs):
        if self.workout:
            workout = self.workout
        elif self.exercise:
            exercise = self.exercise

        super().delete(*args, **kwargs)

        if self.workout:
            workout.likes_count = Favourite.objects.filter(workout=workout).count()
            workout.save()
        elif self.exercise:
            exercise.likes_count = Favourite.objects.filter(exercise=exercise).count()
            exercise.save()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, null=True, blank=True)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.workout:
            return f"Comentario: {self.user.username} - Rutina: {self.workout.workoutName}"
        elif self.exercise:
            return f"Comentario: {self.user.username} - Ejercicio: {self.exercise.exerciseName}"
        return "Comentario sin asociación"

    class Meta:
        ordering = ('date_added', )