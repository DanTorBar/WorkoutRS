from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WorkoutViewSet,
    WorkoutSearchAPIView,
    WorkoutTermSearchAPIView,
    WorkoutDetailAPIView
)

router = DefaultRouter()
router.register(r'workouts', WorkoutViewSet, basename='workout')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', WorkoutSearchAPIView.as_view(), name='workout-search'),
    path('term-search/', WorkoutTermSearchAPIView.as_view(), name='workout-term-search'),
    path('<int:pk>/detail/', WorkoutDetailAPIView.as_view(), name='workout-detail'),
]
