from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
    from django.apps import AppConfig

    def ready(self):
        # Import your signals here so they are registered only when the app is ready.
        import myapp.signals

