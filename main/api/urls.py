# main/api/urls.py
from django.urls import include, path

urlpatterns = [
    path('exercises/', include('main.api.exercises.urls')),
    path('workouts/',  include('main.api.workouts.urls')),
    path('users/',     include('main.api.users.urls')),
    path('imports/',   include('main.api.imports.urls')),
    path('social/',    include('main.api.social.urls')),
]