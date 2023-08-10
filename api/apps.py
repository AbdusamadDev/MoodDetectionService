from django.apps import AppConfig
import os

default_app_config = 'api.apps.ApiConfig'


class ApiConfig(AppConfig):
    name = 'api'
    path = os.path.join(os.path.dirname(__file__))
