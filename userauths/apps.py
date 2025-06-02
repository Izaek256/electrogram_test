from django.apps import AppConfig


class UserauthsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userauths'

    def ready(self):
        import userauths.signals  # Import the signals module
