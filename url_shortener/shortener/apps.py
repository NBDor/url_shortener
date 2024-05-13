from django.apps import AppConfig
from .queue_manager import start_worker_threads


class ShortenerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shortener'

    def ready(self):
        start_worker_threads()


