# WorkoutRS/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # API REST (versión 1)
    path('api/v1/', include('main.api.urls')),
]
