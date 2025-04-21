from unittest.mock import ANY

import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from gotale.models import Game


@pytest.fixture
@pytest.mark.django_db
def game_fixture(scenario_fixture, user1):
    return baker.make(
        Game,
        scenario=scenario_fixture,
        # TODO: the current step shoud be set on model level during creation
        current_step=scenario_fixture.root_step,
        user=user1,
    )


def test_game_viewset_retrieve_success():
    pass


def test_game_viewset_retrieve_errors():
    pass


@pytest.mark.django_db
def test_game_viewset_create_success(auth_client1, user1, scenario_fixture):
    response = auth_client1.post(
        reverse("game-list"),
        data={"scenario": scenario_fixture.id},
    )

    assert (response.status_code, response.json()) == (
        status.HTTP_201_CREATED,
        {
            "created": ANY,
            "current_step": {
                "choices": [
                    {
                        "id": "01234567-89ab-cdef-0123-000000000011",
                        "text": "Go to child 1",
                    },
                    {
                        "id": "01234567-89ab-cdef-0123-000000000022",
                        "text": "Go to child 2",
                    },
                ],
                "description": None,
                "id": "01234567-89ab-cdef-0123-111111111111",
                "location": None,
                "title": "Root Step",
            },
            "scenario": {
                "author": {
                    "created": ANY,
                    "email": "",
                    "first_name": "",
                    "id": str(user1.id),
                    "last_name": "",
                    "modified": ANY,
                    "username": "user1",
                },
                "created": ANY,
                "description": "Test Description",
                "id": str(scenario_fixture.id),
                "modified": ANY,
                "root_step": {
                    "choices": [
                        {
                            "id": ANY,
                            "text": "Go to child 1",
                        },
                        {
                            "id": ANY,
                            "text": "Go to child 2",
                        },
                    ],
                    "description": None,
                    "id": scenario_fixture.root_step.id,
                    "location": None,
                    "title": "Root Step",
                },
                "title": "Test Scenario",
            },
            "user": {
                "created": ANY,
                "email": user1.email,
                "first_name": user1.first_name,
                "id": str(user1.id),
                "last_name": user1.last_name,
                "modified": ANY,
                "username": user1.username,
            },
            "id": ANY,
            "modified": ANY,
        },
    )

    responseJson = response.json()

    assert Game.objects.filter(pk=responseJson["id"]).exists()
    assert (
        str(Game.objects.get(pk=responseJson["id"]).current_step.id)
        == scenario_fixture.root_step.id
    )


@pytest.mark.parametrize(
    "data, expected_status_code, expected_response",
    [
        pytest.param(
            {},
            status.HTTP_400_BAD_REQUEST,
            {
                "scenario": [
                    "This field is required.",
                ],
            },
            id="empty_payload",
        ),
        pytest.param(
            {"scenario": "999"},
            status.HTTP_400_BAD_REQUEST,
            {
                "scenario": [
                    "“999” is not a valid UUID.",
                ],
            },
            id="invalid_uuid",
        ),
        pytest.param(
            {"scenario": "01234567-89ab-cdef-0123-000000000999"},
            status.HTTP_400_BAD_REQUEST,
            {
                "scenario": [
                    'Invalid pk "01234567-89ab-cdef-0123-000000000999" - object does not exist.',
                ],
            },
            id="scenario_not_exists",
        ),
    ],
)
@pytest.mark.django_db
def test_game_viewset_create_errors(
    auth_client1,
    user1,
    scenario_fixture,
    data,
    expected_status_code,
    expected_response,
):
    response = auth_client1.post(reverse("game-list"), data=data)

    assert (response.status_code, response.json()) == (
        expected_status_code,
        expected_response,
    )


def test_game_viewset_update_success():
    # TODO
    pass


def test_game_viewset_update_errors():
    # TODO
    pass


def test_game_viewset_destroy_success():
    # TODO
    pass


def test_game_viewset_destroy_errors():
    # TODO
    pass


@pytest.mark.django_db
def test_game_viewset_current_step_get_success(admin_client, game_fixture):
    response = admin_client.get(
        reverse("game-current-step", kwargs={"pk": game_fixture.id})
    )

    assert (response.status_code, response.json()) == (
        status.HTTP_200_OK,
        {
            "description": None,
            "location": None,
            "title": "Root Step",
            "choices": [
                {
                    "id": "01234567-89ab-cdef-0123-000000000011",
                    "text": "Go to child 1",
                },
                {
                    "id": "01234567-89ab-cdef-0123-000000000022",
                    "text": "Go to child 2",
                },
            ],
            "id": "01234567-89ab-cdef-0123-111111111111",
        },
    )


# TODO: invalid choice
# TODO: user that is not in the game
# TODO: step_get on game ended
def test_game_viewset_current_step_get_errors():
    pass


def test_game_viewset_current_step_post_success():
    pass


# TODO: invalid choice
# TODO: user that is not in the game
# TODO: step_post on game ended
def test_game_viewset_current_step_post_errors():
    pass
