from django.db import models
from django.contrib.auth.models import User
from main.models.exercise import Exercise


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
