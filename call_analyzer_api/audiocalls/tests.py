import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from audiocalls.models import Call, UploadedAudioFile
from users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="user@test.com", password="pw!")


def upload_file_url():
    return reverse("audiocalls:upload_file")


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
