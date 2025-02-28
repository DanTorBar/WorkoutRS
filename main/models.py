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
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    workoutName = models.TextField(verbose_name="Workout name")
    workoutCategory = models.CharField(max_length=200, verbose_name="Workout Category", null=True)
    level = models.CharField(max_length=30, verbose_name="Level", null=True)
    gender = models.CharField(max_length=30, verbose_name="Gender", null=True)
    bodyPart = models.CharField(max_length=100, verbose_name="Body Part", null=True)
    description = models.TextField(verbose_name="Description", null=True, blank=True)

    # # Relación con Ejercicios para cada día
    # day1 = models.ManyToManyField(Exercise, related_name="day1_routine", blank=True)
    # day2 = models.ManyToManyField(Exercise, related_name="day2_routine", blank=True)
    # day3 = models.ManyToManyField(Exercise, related_name="day3_routine", blank=True)
    # day4 = models.ManyToManyField(Exercise, related_name="day4_routine", blank=True)
    # day5 = models.ManyToManyField(Exercise, related_name="day5_routine", blank=True)
    # day6 = models.ManyToManyField(Exercise, related_name="day6_routine", blank=True)
    # day7 = models.ManyToManyField(Exercise, related_name="day7_routine", blank=True)

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


class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    weight = models.FloatField(verbose_name='Weight', null=True)
    height = models.FloatField(verbose_name='Height', null=True)
    age = models.IntegerField(verbose_name='Age', null=True)
    BMI = models.FloatField(verbose_name='BMI', null=True)
    activityLevel = models.CharField(max_length=100, verbose_name='Activity Level', null=True)
    goals = models.CharField(max_length=100, verbose_name='Goal', null=True)
    conditions = models.TextField(verbose_name='Conditions', null=True)
    
    def __str__(self):
        return self.user.username

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
        unique_together = ('workout', 'exercise')



class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, null=True, blank=True)
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