from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import FavouriteViewSet

router = DefaultRouter()
router.register(r'favourites', FavouriteViewSet, basename='favourite')

urlpatterns = [
    path('', include(router.urls)),
]
