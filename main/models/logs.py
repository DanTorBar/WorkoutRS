from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class ViewLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='view_logs'
    )
    # apuntar genérico a Exercise o Workout
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.user.username} viewed {self.content_type} {self.object_id}"


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('IMPORT',  'Importación de datos'),
        ('DELETE',  'Borrado de datos'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    detail = models.TextField(blank=True, help_text="Detalles adicionales en JSON o texto.")

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} {self.action} at {self.timestamp}"

