from django.db import models

class WorkoutCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class ExerciseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Muscle(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Level(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Level")

    def __str__(self):
        return self.name


class Gender(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Gender")

    def __str__(self):
        return self.name


class BodyParts(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Body Parts")

    def __str__(self):
        return self.name


class Exercise(models.Model):
    idExercise = models.AutoField(primary_key=True)
    name = models.TextField(verbose_name='Exercise name')
    description = models.TextField(verbose_name='Description')
    exerciseCategory = models.ForeignKey(ExerciseCategory, on_delete=models.SET_NULL, null=True, verbose_name='Exercise Category')
    priMuscles = models.ManyToManyField(Muscle, related_name='primary', verbose_name='Primary Muscles')
    secMuscles = models.ManyToManyField(Muscle, related_name='secondary', verbose_name='Secondary Muscles')
    video = models.TextField(verbose_name='Video')
    instructions = models.TextField(verbose_name='Instructions')
    tags = models.ManyToManyField(Tag, verbose_name='Tags')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name', )

class Workout(models.Model):
    name = models.CharField(max_length=200, verbose_name="Workout name")
    workoutCategory = models.ForeignKey(WorkoutCategory, on_delete=models.SET_NULL, null=True, verbose_name="Workout Category")
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, verbose_name="Level")
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, verbose_name="Gender")
    bodyParts = models.ManyToManyField(BodyParts, verbose_name="Body Parts")
    description = models.TextField(verbose_name="Description")

    # Relación con Ejercicios para cada día
    dia_1 = models.ManyToManyField(Exercise, related_name="rutinas_dia_1", blank=True)
    dia_2 = models.ManyToManyField(Exercise, related_name="rutinas_dia_2", blank=True)
    dia_3 = models.ManyToManyField(Exercise, related_name="rutinas_dia_3", blank=True)
    dia_4 = models.ManyToManyField(Exercise, related_name="rutinas_dia_4", blank=True)
    dia_5 = models.ManyToManyField(Exercise, related_name="rutinas_dia_5", blank=True)
    dia_6 = models.ManyToManyField(Exercise, related_name="rutinas_dia_6", blank=True)
    dia_7 = models.ManyToManyField(Exercise, related_name="rutinas_dia_7", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
