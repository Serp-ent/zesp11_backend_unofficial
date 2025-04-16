import pytest
from django.urls import reverse
from rest_framework import status

from backend.gotale.models import Scenario


@pytest.mark.django_db
def test_scenario_viewset_list_success(anon_client, user1):
    Scenario.objects.create(title="Test Scenario", author=user1)
    url = reverse("scenario-list")
    response = anon_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0


@pytest.mark.django_db
def test_scenario_viewset_create_success(anon_client):
    url = reverse("scenario-list")
    data = {"title": "New Scenario"}

    response = anon_client.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not Scenario.objects.filter(title="New Scenario").exists()


@pytest.mark.django_db
def test_anon_can_retrieve_scenario(anon_client, user1):
    scenario = Scenario.objects.create(title="Test Scenario", author=user1)
    url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
    response = anon_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Test Scenario"


@pytest.mark.django_db
def test_auth_nonowner_cannot_update_scenario(auth_client1, user2):
    scenario = Scenario.objects.create(title="Test Scenario", author=user2)
    url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
    data = {"title": "Updated Name"}
    response = auth_client1.patch(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_owner_can_update_scenario(auth_client1, user1):
    scenario = Scenario.objects.create(title="Test Scenario", author=user1)
    url = reverse("scenario-detail", kwargs={"pk": scenario.id})
    data = {"title": "Updated Name"}
    response = auth_client1.patch(url, data)
    assert response.status_code == status.HTTP_200_OK

    scenario.refresh_from_db()
    assert scenario.title == "Updated Name"


@pytest.mark.django_db
def test_admin_can_update_scenario(admin_client, user1):
    scenario = Scenario.objects.create(title="Test Scenario", author=user1)
    url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
    data = {"title": "Updated title"}
    response = admin_client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    scenario.refresh_from_db()
    assert scenario.title == "Updated title"


@pytest.mark.django_db
def test_owner_can_delete_scenario(auth_client1, user1):
    scenario = Scenario.objects.create(title="Test Scenario", author=user1)
    url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
    response = auth_client1.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Scenario.objects.filter(pk=scenario.pk).exists()


@pytest.mark.django_db
def test_admin_can_delete_scenario(admin_client, user1):
    scenario = Scenario.objects.create(title="Test Scenario", author=user1)
    url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
    response = admin_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Scenario.objects.filter(pk=scenario.pk).exists()


@pytest.mark.django_db
def test_auth_nonowner_cannot_delete_scenario(auth_client1, user2):
    scenario = Scenario.objects.create(title="Test Scenario", author=user2)
    url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
    response = auth_client1.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_scenario_viewset_retrieve_success():
    pass


def test_scenario_viewset_retrieve_errors():
    pass


def test_scenario_viewset_create_errors():
    pass


def test_scenario_viewset_update_success():
    pass


def test_scenario_viewset_update_errors():
    pass


def test_scenario_viewset_destroy_success():
    pass


def test_scenario_viewset_destroy_errors():
    pass
