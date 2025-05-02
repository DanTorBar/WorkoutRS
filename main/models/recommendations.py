from django.db import models
from django.contrib.auth.models import User

class RecommendCache(models.Model):
    """
    Guarda recomendaciones precalculadas para un usuario,
    con un tipo de ítem (ejercicio o rutina), identificador y puntuación.
    """
    ITEM_TYPES = [
        ('exercise', 'Ejercicio'),
        ('workout', 'Rutina'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    item_type = models.CharField(
        max_length=20,
        choices=ITEM_TYPES
    )
    item_id = models.PositiveIntegerField()
    score = models.FloatField(default=0.0)
    recommended_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'item_type', 'item_id')
        indexes = [
            models.Index(fields=['user', 'item_type', '-score']),
            models.Index(fields=['recommended_at']),
        ]
        ordering = ['-score']

    def __str__(self):
        return f"Recomendación para {self.user.username}: {self.item_type} {self.item_id} (score={self.score:.2f})"
