from django.contrib import admin

from .models import BodyPart, Exercise, ExerciseCategory, Gender, Level, Muscle, Tag, WorkoutCategory

admin.site.register(BodyPart)
admin.site.register(Exercise)
admin.site.register(ExerciseCategory)
admin.site.register(Gender)
admin.site.register(Level)
admin.site.register(Muscle)
admin.site.register(Tag)
admin.site.register(WorkoutCategory)
