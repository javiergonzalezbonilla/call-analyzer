import json
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from audiocalls.models import (
    Call,
    CallStatus,
    TranscriptionRole,
    TranscriptSegment,
    UploadedAudioFile,
)
from call_analyzer_api.taskapp.celery import process_audio_file_task
from users.models import User

RESPONSE_FIXTURE_PATH = (
    Path(__file__).resolve().parent / "services" / "sample_data" / "response.json"
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="user@test.com", password="pw!")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(email="other@test.com", password="pw!")


def upload_file_url():
    return reverse("audiocalls:upload_file")


def list_calls_url():
    return reverse("audiocalls:list_calls")


def call_detail_url(call_id):
    return reverse("audiocalls:call_detail", args=[call_id])


@pytest.mark.django_db
def test_upload_file_creates_call_with_uploaded_audio_file(api_client, user):
    api_client.force_authenticate(user=user)
    audio = SimpleUploadedFile(
        "call.wav", b"fake-audio-bytes", content_type="audio/wav"
    )

    response = api_client.post(upload_file_url(), {"audio": audio}, format="multipart")

    assert response.status_code == status.HTTP_201_CREATED
    assert Call.objects.count() == 1
    call = Call.objects.get()
    assert call.user == user

    assert UploadedAudioFile.objects.count() == 1
    uploaded_audio_file = UploadedAudioFile.objects.get()
    assert uploaded_audio_file.call == call
    assert uploaded_audio_file.type == "audio/wav"
    assert uploaded_audio_file.size == len(b"fake-audio-bytes")


@pytest.mark.django_db
@patch("audiocalls.views.process_audio_file_task")
def test_upload_file_triggers_process_audio_file_task(mock_task, api_client, user):
    api_client.force_authenticate(user=user)
    audio = SimpleUploadedFile(
        "call.wav", b"fake-audio-bytes", content_type="audio/wav"
    )

    response = api_client.post(upload_file_url(), {"audio": audio}, format="multipart")

    assert response.status_code == status.HTTP_201_CREATED
    call = Call.objects.get()
    mock_task.delay.assert_called_once_with(call.call_id)


@pytest.mark.django_db
@patch("call_analyzer_api.taskapp.celery.boto3.client")
def test_process_audio_file_task_persists_transcript_and_related_objects(
    mock_boto_client, user
):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    call = Call.objects.create(user=user)
    audio = SimpleUploadedFile(
        "call.wav", b"fake-audio-bytes", content_type="audio/wav"
    )
    UploadedAudioFile.objects.create(
        call=call, audio=audio, size=audio.size, type="audio/wav", path=audio.name
    )

    process_audio_file_task(call.call_id)

    with open(RESPONSE_FIXTURE_PATH) as f:
        response = json.load(f)

    results = response["results"]
    alternative = results["channels"][0]["alternatives"][0]
    paragraphs = alternative["paragraphs"]["paragraphs"]
    expected_topics = {
        topic["topic"]
        for segment in results.get("topics", {}).get("segments", [])
        for topic in segment.get("topics", [])
    }

    call.refresh_from_db()
    assert call.status == CallStatus.COMPLETED
    assert call.transcript == alternative["transcript"]
    assert call.summary == results["summary"]["short"]

    segments = TranscriptSegment.objects.filter(call=call)
    assert segments.count() == len(paragraphs)

    expected_role_count = sum(len(paragraph["sentences"]) for paragraph in paragraphs)
    assert (
        TranscriptionRole.objects.filter(transcript_segment__call=call).count()
        == expected_role_count
    )

    assert set(call.tags.values_list("name", flat=True)) == expected_topics
    mock_s3.upload_fileobj.assert_called_once()


@pytest.mark.django_db
def test_upload_file_requires_authentication(api_client):
    audio = SimpleUploadedFile(
        "call.wav", b"fake-audio-bytes", content_type="audio/wav"
    )

    response = api_client.post(upload_file_url(), {"audio": audio}, format="multipart")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Call.objects.count() == 0


@pytest.mark.django_db
def test_upload_file_requires_audio_field(api_client, user):
    api_client.force_authenticate(user=user)

    response = api_client.post(upload_file_url(), {}, format="multipart")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Call.objects.count() == 0


@pytest.mark.django_db
def test_list_calls_returns_only_the_authenticated_users_calls(
    api_client, user, other_user
):
    call = Call.objects.create(user=user)
    Call.objects.create(user=other_user)
    api_client.force_authenticate(user=user)

    response = api_client.get(list_calls_url())

    assert response.status_code == status.HTTP_200_OK
    assert [c["call_id"] for c in response.data] == [str(call.call_id)]


@pytest.mark.django_db
def test_list_calls_requires_authentication(api_client):
    response = api_client.get(list_calls_url())

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_call_detail_returns_the_call(api_client, user):
    call = Call.objects.create(user=user)
    api_client.force_authenticate(user=user)

    response = api_client.get(call_detail_url(call.call_id))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["call_id"] == str(call.call_id)


@pytest.mark.django_db
def test_call_detail_returns_404_for_another_users_call(api_client, user, other_user):
    call = Call.objects.create(user=other_user)
    api_client.force_authenticate(user=user)

    response = api_client.get(call_detail_url(call.call_id))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_call_detail_returns_404_for_unknown_call(api_client, user):
    api_client.force_authenticate(user=user)

    response = api_client.get(call_detail_url(uuid.uuid4()))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_call_detail_requires_authentication(api_client, user):
    call = Call.objects.create(user=user)

    response = api_client.get(call_detail_url(call.call_id))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
