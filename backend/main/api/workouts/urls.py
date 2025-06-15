from rest_framework.routers import DefaultRouter
from .views import WorkoutViewSet, workout_options
from django.urls import path

router = DefaultRouter()
router.register(r'', WorkoutViewSet, basename='workout')

urlpatterns = [
    path('options/', workout_options, name='workout-options'),
] + router.urls
