"""Celery app config."""

import os
from celery import Celery
from django.apps import apps, AppConfig
from django.conf import settings

if not settings.configured:
    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "call_analyzer_api.settings.local"
    )  # pragma: no cover


app = Celery("call_analyzer_api")
# Using a string here means the worker will not have to
# pickle the object when using Windows.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")


class CeleryAppConfig(AppConfig):
    name = "call_analyzer_api.taskapp"
    verbose_name = "Celery Config"

    def ready(self):
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        app.autodiscover_tasks(lambda: installed_apps, force=True)


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")  # pragma: no cover


@app.task(bind=True)
def process_audio_file_task(self, call_id):
    from audiocalls.models import Call

    call = Call.objects.get(call_id=call_id)
    uploaded_file = call.uploaded_file

    audio = uploaded_file.audio.open("rb")

    

    print("hello")
    print(audio)

    # SttServiceFactory().get_service().transcript(uploaded_file)
