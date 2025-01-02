from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class CategoriaEjercicio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Musculo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Etiqueta(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Nivel(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nivel")

    def __str__(self):
        return self.nombre


class Genero(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Género")

    def __str__(self):
        return self.nombre


class ParteCuerpo(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Parte del Cuerpo")

    def __str__(self):
        return self.nombre


class Ejercicio(models.Model):
    idEjercicio = models.AutoField(primary_key=True)
    nombre = models.TextField(verbose_name='Nombre')
    descripcion = models.TextField(verbose_name='Descripción')
    categoriaEjercicio = models.ForeignKey(CategoriaEjercicio, on_delete=models.SET_NULL, null=True, verbose_name='Categoría')
    musculosPri = models.ManyToManyField(Musculo, related_name='primarios', verbose_name='Músculos Primarios')
    musculosSec = models.ManyToManyField(Musculo, related_name='secundarios', verbose_name='Músculos Secundarios')
    video = models.TextField(verbose_name='Video')
    instrucciones = models.TextField(verbose_name='Instrucciones')
    etiquetas = models.ManyToManyField(Etiqueta, verbose_name='Etiquetas')

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ('nombre', )

class Rutina(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la Rutina")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, verbose_name="Categoría")
    nivel = models.ForeignKey(Nivel, on_delete=models.SET_NULL, null=True, verbose_name="Nivel")
    genero = models.ForeignKey(Genero, on_delete=models.SET_NULL, null=True, verbose_name="Género")
    partes_cuerpo = models.ManyToManyField(ParteCuerpo, verbose_name="Partes del Cuerpo Trabajadas")
    descripcion = models.TextField(verbose_name="Descripción")

    # Relación con Ejercicios para cada día
    dia_1 = models.ManyToManyField(Ejercicio, related_name="rutinas_dia_1", blank=True)
    dia_2 = models.ManyToManyField(Ejercicio, related_name="rutinas_dia_2", blank=True)
    dia_3 = models.ManyToManyField(Ejercicio, related_name="rutinas_dia_3", blank=True)
    dia_4 = models.ManyToManyField(Ejercicio, related_name="rutinas_dia_4", blank=True)
    dia_5 = models.ManyToManyField(Ejercicio, related_name="rutinas_dia_5", blank=True)
    dia_6 = models.ManyToManyField(Ejercicio, related_name="rutinas_dia_6", blank=True)
    dia_7 = models.ManyToManyField(Ejercicio, related_name="rutinas_dia_7", blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']
