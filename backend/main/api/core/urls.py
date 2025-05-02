from django.urls import path
from .views import (
    PopulateDatabaseAPIView,
)

urlpatterns = [
    path('populate/',                  PopulateDatabaseAPIView.as_view(),    name='populate-db'),
]
