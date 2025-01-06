from main import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('populate/', views.populateDatabase),
    path('buscar_ejercicio_nombre_instrucciones/', views.search_ex_name_instructions),
    path('buscar_ejercicios/', views.search_ex),
    path('ejercicio/<int:id>', views.exercise_detail),
    path('buscar_rutina_nombre_descripcion/', views.search_wt_name_description),
    path('buscar_rutinas/', views.search_wt),
    path('rutina/<str:link>', views.workout_detail),

]
