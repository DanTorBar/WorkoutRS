from rest_framework.routers import DefaultRouter
from .views import ExerciseViewSet, exercise_options
from django.urls import path

router = DefaultRouter()
router.register(r'', ExerciseViewSet, basename='exercise')

urlpatterns = [
    path('options/', exercise_options, name='exercise-options'),
] + router.urls
