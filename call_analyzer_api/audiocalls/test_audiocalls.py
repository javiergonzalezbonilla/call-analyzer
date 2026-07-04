import uuid

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
def test_call_detail_returns_404_for_another_users_call(
    api_client, user, other_user
):
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
