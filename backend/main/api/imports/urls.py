from django.urls import path
from .views import GenericImportAPIView, PreImportAPIView

urlpatterns = [
    path('', GenericImportAPIView.as_view(), name='import-health-data'),
    path('preimport/', PreImportAPIView.as_view(), name='preimport-health-data'),
]