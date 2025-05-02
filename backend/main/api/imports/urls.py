from django.urls import path
from .views import GenericImportAPIView

urlpatterns = [
    path('', GenericImportAPIView.as_view(), name='import-health-data'),
]