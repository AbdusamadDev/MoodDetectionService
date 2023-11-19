from django.apps import AppConfig

default_app_config = 'api.apps.ApiConfig'


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        import api.signals  # type: ignore
