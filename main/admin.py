from django.contrib import admin

from .models import Workout, Exercise, Muscle

admin.site.register(Exercise)
admin.site.register(Muscle)
admin.site.register(Workout)