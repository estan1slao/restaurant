from django.db import models


class ModerationSettings(models.Model):
    MODERATION_CHOICES = [
        ('manual', 'Manual'),
        ('auto', 'Auto'),
    ]
    moderation_type = models.CharField(max_length=10, choices=MODERATION_CHOICES, default='manual')
