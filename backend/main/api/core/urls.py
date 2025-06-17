from django.urls import path
from .views import (
    PopulateDatabaseAPIView,
    RecommendExercisesAPIView,
    RecommendWorkoutsAPIView,
)

urlpatterns = [
    path('populate/',                  PopulateDatabaseAPIView.as_view(),    name='populate-db'),
    path('recommend/exercises/',      RecommendExercisesAPIView.as_view(),  name='recommend-exercises'),
    path('recommend/workouts/',       RecommendWorkoutsAPIView.as_view(),   name='recommend-workouts'),
]
