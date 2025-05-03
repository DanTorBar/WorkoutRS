from django.contrib import admin

from main.models.exercise import Exercise, Muscle
from main.models.workout import Workout
from main.models.social import Favourite
from main.models.recommendations import RecommendCache
from main.models.logs import ViewLog, ActivityLog


admin.site.register(Exercise)
admin.site.register(Muscle)
admin.site.register(Workout)
admin.site.register(Favourite)
admin.site.register(RecommendCache)
admin.site.register(ViewLog)
admin.site.register(ActivityLog)