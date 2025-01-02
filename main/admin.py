from django.contrib import admin

from .models import Categoria, CategoriaEjercicio, Musculo, Etiqueta, Nivel, Genero, ParteCuerpo, Ejercicio

admin.site.register(Categoria)
admin.site.register(CategoriaEjercicio)
admin.site.register(Musculo)
admin.site.register(Etiqueta)
admin.site.register(Nivel)
admin.site.register(Genero)
admin.site.register(ParteCuerpo)
admin.site.register(Ejercicio)