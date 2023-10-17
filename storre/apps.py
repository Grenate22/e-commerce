from django.apps import AppConfig


class StorreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'storre'

    def ready(self) -> None:
        import storre.signals.handlers
