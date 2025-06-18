import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WorkoutRS.settings')
django.setup()

from django.contrib.auth.models import User

# Crear o actualizar usuario admin
admin_user, created = User.objects.update_or_create(
    username='admin',
    defaults={
        'email': 'admin@example.com',
        'is_superuser': True,
        'is_staff': True,
        'is_active': True,
    }
)
admin_user.set_password('password123')
admin_user.save()
print(f"Usuario admin {'creado' if created else 'actualizado'}.")

# Crear o actualizar usuario normal
normal_user, created = User.objects.update_or_create(
    username='testuser',
    defaults={
        'email': 'usuario@example.com',
        'is_superuser': False,
        'is_staff': False,
        'is_active': True,
    }
)
normal_user.set_password('password123')
normal_user.save()
print(f"Usuario normal {'creado' if created else 'actualizado'}.")
