from django.apps import AppConfig
import threading
class TestConfig(AppConfig):
    name = 'tests'

    def ready(self):
        from .views import start_scheduler
        start_scheduler()