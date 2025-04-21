from unittest.mock import ANY

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from gotale.models import Choice, Scenario, Step

User = get_user_model()


@pytest.fixture
@pytest.mark.django_db
def user1():
    return baker.make(User, username="user1", password="password1")


@pytest.fixture
@pytest.mark.django_db
def scenario_fixture(user1):
    scenario = baker.make(
        Scenario,
        id="01234567-89ab-cdef-0123-000000000000",
        author=user1,
        title="Test Scenario",
        description="Test Description",
        root_step=None,
    )

    root_step = baker.make(Step, scenario=scenario, title="Root Step")
    scenario.root_step = root_step
    scenario.save()

    child_steps = baker.make(
        Step,
        scenario=scenario,
        _quantity=2,
    )

    choice_data = [
        {"id": 5, "text": "Go to child 1", "next": child_steps[0]},
        {"id": 6, "text": "Go to child 2", "next": child_steps[1]},
    ]

    [
        baker.make(
            Choice,
            step=root_step,
            id=data["id"],
            text=data["text"],
            next=data["next"],
        )
        for data in choice_data
    ]

    return scenario


# @pytest.mark.django_db
# def test_scenario_viewset_list_success(anon_client, user1):
#     Scenario.objects.create(title="Test Scenario", author=user1)
#     url = reverse("scenario-list")
#     response = anon_client.get(url)
#     assert response.status_code == status.HTTP_200_OK
#     assert len(response.data) > 0


# @pytest.mark.django_db
# def test_scenario_viewset_create_success(anon_client):
#     url = reverse("scenario-list")
#     data = {"title": "New Scenario"}

#     response = anon_client.post(url, data)
#     assert response.status_code == status.HTTP_403_FORBIDDEN
#     assert not Scenario.objects.filter(title="New Scenario").exists()


# @pytest.mark.django_db
# def test_anon_can_retrieve_scenario(anon_client, user1):
#     scenario = Scenario.objects.create(title="Test Scenario", author=user1)
#     url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
#     response = anon_client.get(url)
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data["title"] == "Test Scenario"


# @pytest.mark.django_db
# def test_auth_nonowner_cannot_update_scenario(auth_client1, user2):
#     scenario = Scenario.objects.create(title="Test Scenario", author=user2)
#     url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
#     data = {"title": "Updated Name"}
#     response = auth_client1.patch(url, data)
#     assert response.status_code == status.HTTP_403_FORBIDDEN


# @pytest.mark.django_db
# def test_owner_can_update_scenario(auth_client1, user1):
#     scenario = Scenario.objects.create(title="Test Scenario", author=user1)
#     url = reverse("scenario-detail", kwargs={"pk": scenario.id})
#     data = {"title": "Updated Name"}
#     response = auth_client1.patch(url, data)
#     assert response.status_code == status.HTTP_200_OK

#     scenario.refresh_from_db()
#     assert scenario.title == "Updated Name"


# @pytest.mark.django_db
# def test_admin_can_update_scenario(admin_client, user1):
#     scenario = Scenario.objects.create(title="Test Scenario", author=user1)
#     url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
#     data = {"title": "Updated title"}
#     response = admin_client.patch(url, data)
#     assert response.status_code == status.HTTP_200_OK
#     scenario.refresh_from_db()
#     assert scenario.title == "Updated title"


# @pytest.mark.django_db
# def test_owner_can_delete_scenario(auth_client1, user1):
#     scenario = Scenario.objects.create(title="Test Scenario", author=user1)
#     url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
#     response = auth_client1.delete(url)
#     assert response.status_code == status.HTTP_204_NO_CONTENT
#     assert not Scenario.objects.filter(pk=scenario.pk).exists()


# @pytest.mark.django_db
# def test_admin_can_delete_scenario(admin_client, user1):
#     scenario = Scenario.objects.create(title="Test Scenario", author=user1)
#     url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
#     response = admin_client.delete(url)
#     assert response.status_code == status.HTTP_204_NO_CONTENT
#     assert not Scenario.objects.filter(pk=scenario.pk).exists()


# @pytest.mark.django_db
# def test_auth_nonowner_cannot_delete_scenario(auth_client1, user2):
#     scenario = Scenario.objects.create(title="Test Scenario", author=user2)
#     url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
#     response = auth_client1.delete(url)
#     assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_scenario_viewset_retrieve_success(scenario_fixture, anon_client, user1):
    response = anon_client.get(
        reverse("scenario-detail", kwargs={"pk": scenario_fixture.pk})
    )

    assert (response.status_code, response.json()) == (
        status.HTTP_200_OK,
        {
            "author": {
                "email": user1.email,
                "first_name": user1.first_name,
                "id": str(user1.id),
                "last_name": user1.last_name,
                "username": user1.username,
                "created": ANY,
                "modified": ANY,
            },
            "created": ANY,
            "description": "Test Description",
            "id": scenario_fixture.id,
            "modified": ANY,
            "root_step": {
                "description": None,
                "id": 1,
                "choices": [
                    {"id": 5, "text": "Go to child 1"},
                    {"id": 6, "text": "Go to child 2"},
                ],
                "location": None,
                "title": "Root Step",
            },
            "title": "Test Scenario",
        },
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "pk",
    [
        pytest.param("01234567-89ab-cdef-0123-000000000001", id="not_found"),
    ],
)
def test_scenario_viewset_retrieve_errors(anon_client, scenario_fixture, pk):
    response = anon_client.get(reverse("scenario-detail", kwargs={"pk": pk}))

    assert response.status_code == status.HTTP_404_NOT_FOUND


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
