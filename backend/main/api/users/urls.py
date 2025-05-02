from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    CurrentUserAPIView,
    HealthDataPreImportAPIView,
    RevokeHealthDataConsentAPIView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    # Autenticación y registro
    path('register/', RegisterAPIView.as_view(),                     name='user-register'),
    path('login/',    LoginAPIView.as_view(),                        name='user-login'),
    path('logout/',   LogoutAPIView.as_view(),                       name='user-logout'),

    # Usuario actual (GET, PUT, PATCH)
    path('me/',       CurrentUserAPIView.as_view(),                  name='current-user'),

    # Import preview y revocación de consentimiento
    path('<str:service_key>/preimport/', HealthDataPreImportAPIView.as_view(),     name='health-preimport'),
    path('revoke-consent/',            RevokeHealthDataConsentAPIView.as_view(),   name='revoke-consent'),

    # CRUD de usuarios (sólo admin o según permisos de UserViewSet)
    path('', include(router.urls)),
]
