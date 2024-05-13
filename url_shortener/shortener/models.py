from django.db import models
from .constants import SHORTCODE_MAX


class ShortURL(models.Model):
    long_url = models.URLField()
    short_url = models.CharField(max_length=SHORTCODE_MAX, unique=True)
    hits = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.short_url


class AvailableShortURL(models.Model):
    short_url = models.CharField(max_length=SHORTCODE_MAX, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']


class AppConfig(models.Model):
    key = models.CharField(max_length=255, unique=True)
    value = models.CharField(max_length=255)