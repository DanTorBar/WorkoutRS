from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        return self.exerciseName

    class Meta:
        ordering = ('exerciseName', )

class Workout(models.Model):
    workoutName = models.TextField(verbose_name="Workout name")
    workoutCategory = models.CharField(max_length=200, verbose_name="Workout Category", null=True)
    level = models.CharField(max_length=30, verbose_name="Level", null=True)
    gender = models.CharField(max_length=30, verbose_name="Gender", null=True)
    bodyPart = models.CharField(max_length=100, verbose_name="Body Part", null=True)
    description = models.TextField(verbose_name="Description", null=True, blank=True)

    # Relación con Ejercicios para cada día
    day1 = models.ManyToManyField(Exercise, related_name="day1_routine", blank=True)
    day2 = models.ManyToManyField(Exercise, related_name="day2_routine", blank=True)
    day3 = models.ManyToManyField(Exercise, related_name="day3_routine", blank=True)
    day4 = models.ManyToManyField(Exercise, related_name="day4_routine", blank=True)
    day5 = models.ManyToManyField(Exercise, related_name="day5_routine", blank=True)
    day6 = models.ManyToManyField(Exercise, related_name="day6_routine", blank=True)
    day7 = models.ManyToManyField(Exercise, related_name="day7_routine", blank=True)

    def __str__(self):
        return self.workoutName

    class Meta:
        ordering = ['workoutName']


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
