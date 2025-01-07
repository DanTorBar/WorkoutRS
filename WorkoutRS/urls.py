from main import views
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('inicio/', views.index, name='inicio'),
    path('populate/', views.populateDatabase),
    path('buscar_ejercicio_nombre_instrucciones/', views.search_ex_name_instructions),
    path('buscar_ejercicios/', views.search_ex),
    path('ejercicio/<int:id>', views.exercise_detail),
    path('buscar_rutina_nombre_descripcion/', views.search_wt_name_description),
    path('buscar_rutinas/', views.search_wt),
    path('rutina/<str:link>', views.workout_detail),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page="/inicio"), name='logout'),
    path('editar/', views.edit_user, name='editar_usuario'),
    path('perfil/', views.user_profile, name='perfil')

]
