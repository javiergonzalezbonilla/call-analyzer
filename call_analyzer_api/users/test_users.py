import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


def login_url():
    return reverse("users:login")


@pytest.fixture
def admin(db):
    return User.objects.create_user(
        email="admin@test.com", password="pw!", role=User.ROLE_ADMIN
    )


@pytest.mark.django_db
def test_login_returns_token(api_client, admin):
    r = api_client.post(login_url(), {"email": admin.email, "password": "pw!"})
    assert r.status_code == status.HTTP_200_OK
    assert "token" in r.data
    assert r.data["user"]["email"] == admin.email
