from main import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('populate/', views.populateDatabase),
    path('buscar_ejercicio_nombre_instrucciones/', views.search_ex_name_instructions),
    path('buscar_ejercicios/', views.search_ex),

]
