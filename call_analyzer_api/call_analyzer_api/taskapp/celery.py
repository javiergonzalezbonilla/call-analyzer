"""Celery app config."""

import os

import boto3
from celery import Celery
from django.apps import apps, AppConfig
from django.conf import settings
from audiocalls.services.stt import SttServiceFactory

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

    s3 = boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    path = f"audio_files/{uploaded_file.path}"

    with uploaded_file.audio.open("rb") as audio:
        s3.upload_fileobj(audio, settings.AWS_UPLOADED_FILES_BUCKET_NAME, path)

    response = SttServiceFactory.get_service().transcript(path)

    _persist_transcript(call, response)


def _persist_transcript(call, response):
    from audiocalls.models import CallStatus, Tags, TranscriptSegment, TranscriptionRole

    results = response["results"]
    alternative = results["channels"][0]["alternatives"][0]

    call.transcript = alternative["transcript"]
    call.summary = results["summary"]["short"]
    call.status = CallStatus.COMPLETED
    call.save()

    for paragraph in alternative["paragraphs"]["paragraphs"]:
        segment = TranscriptSegment.objects.create(
            call=call,
            start_time=paragraph["start"],
            end_time=paragraph["end"],
        )
        for sentence in paragraph["sentences"]:
            TranscriptionRole.objects.create(
                transcript_segment=segment,
                speaker=str(paragraph["speaker"]),
                start_time=sentence["start"],
                end_time=sentence["end"],
                text=sentence["text"],
            )

    topic_names = {
        topic["topic"]
        for segment in results.get("topics", {}).get("segments", [])
        for topic in segment.get("topics", [])
    }
    for name in topic_names:
        tag, _ = Tags.objects.get_or_create(name=name)
        call.tags.add(tag)
