from django.db import models
from django.contrib.auth.models import User

from main.models.exercise import Exercise
from main.models.workout import Workout


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