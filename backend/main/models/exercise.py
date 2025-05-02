from django.db import models


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
