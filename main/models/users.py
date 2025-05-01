# User related models
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from main.constants import ACTIVITY_LEVEL_CHOICES


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
    ], default='unknown')

    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # --- Objetivos y condiciones ---
    goals         = models.ManyToManyField('Goal', blank=True, verbose_name=_("Objetivos"))
    conditions    = models.ManyToManyField('Condition', blank=True, verbose_name=_("Condiciones"))

    # --- Entornos y equipamiento disponible ---
    equipment     = models.ManyToManyField('Equipment', blank=True, verbose_name=_("Equipamiento"))
    environment   = models.CharField(_("Entorno"), max_length=200, blank=True)

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

class Goal(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Condition(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Equipment(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

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

from django.conf import settings
from django.db import models
