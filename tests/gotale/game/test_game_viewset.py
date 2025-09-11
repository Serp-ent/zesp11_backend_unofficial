from unittest.mock import ANY
from uuid import UUID

import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from gotale.models import Game, GameStatus
from tests.core.test_user_viewset import USER_LIST

GAME_LIST = [
    {
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
        "id": "1ede802f-d69b-41d5-b370-000000000000",
        "scenario": {
            "created_by": USER_LIST[0],
            "created_at": ANY,
            "description": "Test Description",
            "id": "01234567-89ab-cdef-0123-000000000000",
            "modified_at": ANY,
            "modified_by": None,
            "root_step": {
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
            "title": "Test Scenario",
        },
        "user": USER_LIST[0],
    },
    {
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
        "id": "1ede802f-d69b-41d5-b370-000000000001",
        "scenario": {
            "created_by": USER_LIST[0],
            "created_at": ANY,
            "description": "Test Description",
            "id": "01234567-89ab-cdef-0123-000000000000",
            "modified_at": ANY,
            "modified_by": None,
            "root_step": {
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
            "title": "Test Scenario",
        },
        "user": USER_LIST[1],
    },
    {
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
        "id": "1ede802f-d69b-41d5-b370-000000000002",
        "scenario": {
            "created_by": USER_LIST[0],
            "created_at": ANY,
            "description": "Test Description",
            "id": "01234567-89ab-cdef-0123-000000000000",
            "modified_at": ANY,
            "modified_by": None,
            "root_step": {
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
            "title": "Test Scenario",
        },
        "user": USER_LIST[2],
    },
]


@pytest.fixture
@pytest.mark.django_db
def games_fixture(scenario_fixture, users_fixture):
    return Game.objects.bulk_create(
        [
            baker.prepare(
                Game,
                id="1ede802f-d69b-41d5-b370-000000000000",
                scenario=scenario_fixture,
                # TODO: the current step shoud be set on model level during creation
                current_step=scenario_fixture.root_step,
                user=users_fixture[0],
            ),
            baker.prepare(
                Game,
                id="1ede802f-d69b-41d5-b370-000000000001",
                scenario=scenario_fixture,
                current_step=scenario_fixture.root_step,
                user=users_fixture[1],
            ),
            baker.prepare(
                Game,
                id="1ede802f-d69b-41d5-b370-000000000002",
                scenario=scenario_fixture,
                current_step=scenario_fixture.root_step,
                user=users_fixture[2],
            ),
        ]
    )


@pytest.fixture
def game_ended_fixture(games_fixture, scenario_fixture):
    game = games_fixture[0]
    game.current_step = game.current_step.choices.get(
        pk="01234567-89ab-cdef-0123-000000000011"
    ).next

    game.save()
    return game


@pytest.mark.django_db
def test_game_viewset_list_success(auth_client, games_fixture):
    response = auth_client.get(reverse("game-list"))

    assert (response.status_code, response.json()) == (status.HTTP_200_OK, GAME_LIST)


@pytest.mark.django_db
def test_game_viewset_list_errors(auth_client, games_fixture):
    pass


@pytest.mark.django_db
def test_game_viewset_retrieve_success(auth_client, games_fixture):
    response = auth_client.get(
        reverse("game-detail", kwargs={"pk": games_fixture[0].id})
    )

    assert (response.status_code, response.json()) == (
        status.HTTP_200_OK,
        GAME_LIST[0],
    )


@pytest.mark.django_db
def test_game_viewset_retrieve_errors(auth_client):
    response = auth_client.get(
        reverse("game-detail", kwargs={"pk": "1ede802f-d69b-41d5-b370-000000000000"})
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_game_viewset_create_success(auth_client, users_fixture, scenario_fixture):
    response = auth_client.post(
        reverse("game-list"),
        data={"scenario": scenario_fixture.id},
    )

    assert (response.status_code, response.json()) == (
        status.HTTP_201_CREATED,
        GAME_LIST[0] | {"id": ANY},
    )

    response_json = response.json()

    assert Game.objects.filter(pk=response_json["id"]).exists()
    assert (
        str(Game.objects.get(pk=response_json["id"]).current_step.id)
        == scenario_fixture.root_step.id
    )
    assert list(Game.objects.filter(pk=response_json["id"]).values("user")) == [
        {
            "user": UUID(users_fixture[0].id),
        }
    ]


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
    auth_client,
    user1_fixture,
    scenario_fixture,
    data,
    expected_status_code,
    expected_response,
):
    response = auth_client.post(reverse("game-list"), data=data)

    assert (response.status_code, response.json()) == (
        expected_status_code,
        expected_response,
    )


def test_game_viewset_update_success():
    pass


@pytest.mark.parametrize("method", ("put", "patch"))
@pytest.mark.django_db
def test_game_viewset_update_errors(auth_client, games_fixture, method):
    response = getattr(auth_client, method)(
        reverse("game-detail", kwargs={"pk": games_fixture[0].id})
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_game_viewset_destroy_success():
    pass


@pytest.mark.django_db
def test_game_viewset_destroy_errors(auth_client, games_fixture):
    response = auth_client.delete(
        reverse("game-detail", kwargs={"pk": games_fixture[0].id})
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_game_viewset_current_step_get_success(auth_client, games_fixture):
    response = auth_client.get(
        reverse("game-current-step", kwargs={"pk": games_fixture[0].id})
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
            "id": games_fixture[0].current_step.id,
        },
    )


@pytest.mark.django_db
def test_game_viewset_current_step_get_errors(auth_client, game_ended_fixture):
    response = auth_client.get(
        reverse("game-current-step", kwargs={"pk": game_ended_fixture.id})
    )

    assert game_ended_fixture.status == GameStatus.ENDED
    assert (response.status_code, response.json()) == (
        status.HTTP_200_OK,
        {
            "description": None,
            "location": None,
            "title": "Child 1 (ended)",
            "choices": [],
            "id": str(game_ended_fixture.current_step.id),
        },
    )


@pytest.mark.django_db
def test_game_viewset_current_step_post_success(auth_client, games_fixture):
    response = auth_client.post(
        reverse("game-current-step", kwargs={"pk": games_fixture[0].id}),
        data={
            "choice": "01234567-89ab-cdef-0123-000000000011",
        },
    )

    assert (response.status_code, response.json()) == (
        status.HTTP_200_OK,
        {
            "description": None,
            "location": None,
            "title": "Child 1 (ended)",
            "choices": [],
            "id": "01234567-89ab-aaaa-0123-123000000001",
        },
    )
    assert Game.objects.get(id=games_fixture[0].id).status == GameStatus.ENDED


@pytest.mark.parametrize(
    "pk, payload, expected_status_code, expected_response",
    (
        pytest.param(
            "1ede802f-d69b-41d5-b370-999999999999",
            {},
            status.HTTP_404_NOT_FOUND,
            {
                "detail": "No Game matches the given query.",
            },
            id="game-dont-exist",
        ),
        pytest.param(
            "1ede802f-d69b-41d5-b370-000000000001",
            {},
            status.HTTP_400_BAD_REQUEST,
            {
                "choice": [
                    "This field is required.",
                ],
            },
            id="empty-body",
        ),
        pytest.param(
            "1ede802f-d69b-41d5-b370-000000000001",
            {},
            status.HTTP_400_BAD_REQUEST,
            {
                "choice": [
                    "This field is required.",
                ],
            },
            id="empty-body",
        ),
        pytest.param(
            "1ede802f-d69b-41d5-b370-000000000001",
            {
                "choice": "01234567-89ab-cdef-0123-999999999999",
            },
            status.HTTP_404_NOT_FOUND,
            {
                "detail": "No Choice matches the given query.",
            },
            id="invalid-choice",
        ),
        pytest.param(
            "1ede802f-d69b-41d5-b370-000000000000",
            {
                "choice": "01234567-89ab-cdef-0123-000000000011",
            },
            status.HTTP_400_BAD_REQUEST,
            {
                "error": "This game has already ended",
            },
            id="ended-game",
        ),
    ),
)
# TODO: user that is not in the game
@pytest.mark.django_db
def test_game_viewset_current_step_post_errors(
    auth_client,
    game_ended_fixture,
    games_fixture,
    payload,
    expected_status_code,
    expected_response,
    pk,
):
    response = auth_client.post(
        reverse("game-current-step", kwargs={"pk": pk}),
        data=payload,
    )

    assert (response.status_code, response.json()) == (
        expected_status_code,
        expected_response,
    )
    # TODO: check with db that changes were not made
    # assert Game.objects.get(id=pk) == games_fixture
