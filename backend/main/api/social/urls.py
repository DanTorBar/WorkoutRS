from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CommentViewSet, FavouriteViewSet

router = DefaultRouter()
router.register(r'favourites', FavouriteViewSet, basename='favourite')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]
