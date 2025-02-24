import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture
@pytest.mark.django_db
def user1():
    return User.objects.create_user(
        username="user1",
        password="user1",
    )


@pytest.fixture
@pytest.mark.django_db
def user2():
    return User.objects.create_user(
        username="user2",
        password="user2",
    )


@pytest.fixture
@pytest.mark.django_db
def admin_user():
    return User.objects.create_superuser(
        username="admin",
        password="admin",
    )


@pytest.fixture
def anon_client():
    return APIClient()


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def auth_client1(user1):
    client = APIClient()
    client.force_authenticate(user=user1)
    return client


@pytest.fixture
def auth_client2(user2):
    client = APIClient()
    client.force_authenticate(user=user2)
    return client
