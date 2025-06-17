# User related models
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from main.constants import ACTIVITY_LEVEL_CHOICES

GOAL_CHOICES = [
    ("Mejora de la resistencia", "Mejora de la resistencia"),
    ("Pérdida de peso", "Pérdida de peso"),
    ("Mantenimiento de la salud", "Mantenimiento de la salud"),
    ("Mejorar la salud mental", "Mejorar la salud mental"),
    ("Aumentar la fuerza", "Aumentar la fuerza"),
    ("Ganancia muscular", "Ganancia muscular"),
    ("Preparación deportiva", "Preparación deportiva"),
    ("Mejora de la flexibilidad", "Mejora de la flexibilidad"),
    ("Mejorar la movilidad", "Mejorar la movilidad"),
    ("Mejorar la postura", "Mejorar la postura"),
    ("Rehabilitación tras lesión", "Rehabilitación tras lesión")
]

CONDITION_CHOICES = [
    ("Ninguna", "Ninguna"),
    ("Hipertensión", "Hipertensión"),
    ("Diabetes", "Diabetes"),
    ("Asma", "Asma"),
    ("Dolor de espalda", "Dolor de espalda"),
    ("Lesión de rodilla", "Lesión de rodilla"),
    ("Embarazo", "Embarazo"),
    ("Osteoporosis", "Osteoporosis"),
    ("Artritis", "Artritis"),
    ("Enfermedad cardíaca", "Enfermedad cardíaca"),
    ("Sobrepeso", "Sobrepeso"),
    ("Ansiedad", "Ansiedad"),
    ("Depresión", "Depresión"),
    ("EPOC", "EPOC"),
    ("Escoliosis", "Escoliosis"),
    ("Lesión", "Lesión"),
    ("Otra", "Otra"),
]

EQUIPMENT_CHOICES = [
    ("Casa", "Casa"),
    ("Gimnasio", "Gimnasio"),
    ("AireLibre", "Aire libre"),
    ("Mancuernas", "Mancuernas"),
    ("Barras", "Barras"),
    ("Máquinas", "Máquinas"),
    ("Poleas", "Poleas"),
    ("BandasElásticas", "Bandas elásticas"),
    ("Kettlebell", "Kettlebell"),
    ("TRX", "TRX"),
    ("Banco", "Banco"),
    ("Esterilla", "Esterilla"),
    ("CuerdaSaltadora", "Cuerda saltadora"),
    ("BalónMedicinal", "Balón medicinal"),
]

ENVIRONMENT_CHOICES = [
    ("Casa", "Casa"),
    ("Gimnasio", "Gimnasio"),
    ("AireLibre", "Aire libre"),
]


class HealthProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # --- Datos personales ---
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=[
        ('masculino', 'MASCULINO'),
        ('femenino', 'FEMENINO'),
        ('otro', 'OTRO'),
        ('desconocido', 'DESCONOCIDO'),
    ], default='desconocido')

    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # --- Objetivos y condiciones ---
    goals = models.TextField(blank=True, verbose_name=_("Objetivos"), help_text="Separados por coma. Opciones: " + ', '.join([g[0] for g in GOAL_CHOICES]))
    conditions = models.TextField(blank=True, verbose_name=_("Condiciones"), help_text="Separados por coma. Opciones: " + ', '.join([c[0] for c in CONDITION_CHOICES]))

    # --- Entornos y equipamiento disponible ---
    equipment = models.TextField(blank=True, verbose_name=_("Equipamiento"), help_text="Separados por coma. Opciones: " + ', '.join([e[0] for e in EQUIPMENT_CHOICES]))
    environment = models.TextField(blank=True, verbose_name=_("Entorno"), help_text="Separados por coma. Opciones: " + ', '.join([e[0] for e in ENVIRONMENT_CHOICES]))

    # --- Datos importados (minutos semanales) ---
    imported_neat_min = models.PositiveIntegerField(null=True, blank=True, help_text="Actividad general (NEAT)")
    imported_cardio_mod_min = models.PositiveIntegerField(null=True, blank=True, help_text="Cardio moderado")
    imported_cardio_vig_min = models.PositiveIntegerField(null=True, blank=True, help_text="Cardio vigoroso")

    # --- Fallback manual (niveles 0–5) ---
    neat_level = models.PositiveSmallIntegerField(choices=ACTIVITY_LEVEL_CHOICES, default=0)
    cardio_mod_level = models.PositiveSmallIntegerField(choices=ACTIVITY_LEVEL_CHOICES, default=0)
    cardio_vig_level = models.PositiveSmallIntegerField(choices=ACTIVITY_LEVEL_CHOICES, default=0)
    strength_level = models.PositiveSmallIntegerField(choices=ACTIVITY_LEVEL_CHOICES, default=0)

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"HealthProfile of {self.user.username}"

    def get_goals_list(self):
        return [g.strip() for g in self.goals.split(',') if g.strip()]

    def set_goals_list(self, goals_list):
        self.goals = ','.join(goals_list)

    def get_conditions_list(self):
        return [c.strip() for c in self.conditions.split(',') if c.strip()]

    def set_conditions_list(self, cond_list):
        self.conditions = ','.join(cond_list)

    def get_equipment_list(self):
        return [e.strip() for e in self.equipment.split(',') if e.strip()]

    def set_equipment_list(self, eq_list):
        self.equipment = ','.join(eq_list)

    def get_environment_list(self):
        return [e.strip() for e in self.environment.split(',') if e.strip()]

    def set_environment_list(self, env_list):
        self.environment = ','.join(env_list)

class HealthDataConsent(models.Model):
    """
    Guarda el consentimiento explícito del usuario al tratamiento de sus datos de salud.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="health_data_consent"
    )
    given = models.BooleanField(
        default=False,
        help_text="¿Ha dado el usuario consentimiento para procesar sus datos de salud?"
    )
    given_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Cuándo dio el usuario su consentimiento"
    )

    def __str__(self):
        return f"{self.user.username}: consent={self.given}"
