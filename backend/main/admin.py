from django.contrib import admin

from main.models.exercise import Exercise, Muscle
from main.models.workout import Workout
from main.models.social import Favourite


admin.site.register(Exercise)
admin.site.register(Muscle)
admin.site.register(Workout)
admin.site.register(Favourite)