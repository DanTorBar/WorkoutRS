from django.shortcuts import render
from django.urls import reverse
from main.forms import CustomUserCreationForm, EditUserForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


# Usuarios

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse('inicio'))
        else:
            print(form.errors)  # Esto mostrará los errores en la consola

    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('inicio')
        else:
            return render(request, 'login.html', {'error': 'Invalid login'})
    return render(request, 'login.html')


@login_required
def user_profile(request):
    return render(request, 'perfil.html', {'user': request.user})


@login_required
def edit_user(request):
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('perfil')
    else:
        form = EditUserForm(instance=request.user)
    
    return render(request, 'editar_usuario.html', {'form': form})

