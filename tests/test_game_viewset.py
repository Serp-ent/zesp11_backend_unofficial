import pytest
from django.urls import reverse
from rest_framework import status

from gotale.models import Game, History


@pytest.mark.django_db
def test_read_games_anonymous(anon_client, create_game):
    list_url = reverse("game-list")
    detail_url = reverse("game-detail", args=[create_game.id])

    response = anon_client.get(list_url)
    assert response.status_code == status.HTTP_200_OK

    response = anon_client.get(detail_url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_game_authenticated(auth_client1, scenario_setup, user1):
    url = reverse("game-list")
    # Build nested dictionary for current_step according to what the serializer expects.
    current_step_data = {
        "id": scenario_setup["step1"].id,
        "title": scenario_setup["step1"].title,
        "description": scenario_setup["step1"].description,
        "scenario": scenario_setup["scenario"].id,
        "location": scenario_setup["step1"].location.id,
    }
    data = {
        "scenario": scenario_setup["scenario"].id,
        "current_step": current_step_data,
        "user": user1.id,
    }
    response = auth_client1.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.data

    # Check that the created game has its user set correctly.
    game_id = response.data.get("id")
    game = Game.objects.get(pk=game_id)
    assert game.user == user1

    # Check that an active session was auto-created.
    active_sessions = game.sessions.filter(is_active=True)
    assert active_sessions.exists(), "Active session should be created for the game"


@pytest.mark.django_db
def test_current_step_get_in_game_user(auth_client1, create_game, scenario_setup):
    # auth_client1 is logged in as user1; the game created has user=user1 and an active session.
    url = reverse("game-current-step", args=[create_game.id])
    response = auth_client1.get(url)
    assert response.status_code == status.HTTP_200_OK
    # Verify that the current step matches step1
    assert response.data.get("id") == scenario_setup["step1"].id


@pytest.mark.django_db
def test_current_step_get_not_in_game_user(auth_client2, create_game):
    # auth_client2 is logged in as user2 (not owner, no active session for this game)
    url = reverse("game-current-step", args=[create_game.id])
    response = auth_client2.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_current_step_post_valid_choice(auth_client1, create_game, scenario_setup):
    url = reverse("game-current-step", args=[create_game.id])
    data = {"choice_id": scenario_setup["choice"].id}

    response = auth_client1.post(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK

    # Verify that the game’s current_step is updated to step2.
    create_game.refresh_from_db()
    assert create_game.current_step.id == scenario_setup["step2"].id

    # Verify that a history record was created.
    history_exists = History.objects.filter(
        session__game=create_game,
        step=scenario_setup["step1"],
        choice=scenario_setup["choice"],
    ).exists()
    assert history_exists


@pytest.mark.django_db
def test_current_step_post_invalid_choice(auth_client1, create_game):
    url = reverse("game-current-step", args=[create_game.id])
    # Provide an invalid choice ID.
    data = {"choice_id": 9999}
    response = auth_client1.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# @pytest.mark.django_db
# def test_current_step_post_on_ended_game(auth_client1, create_game, scenario_setup):
#     # End the game.
#     create_game.end = timezone.now()
#     create_game.save()

#     url = reverse("game-current-step", args=[create_game.id])
#     data = {"choice_id": scenario_setup["choice"].id}
#     response = auth_client1.post(url, data, format="json")
#     assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_game_viewset_retrieve_success():
    pass


def test_game_viewset_retrieve_errors():
    pass


def test_game_viewset_create_errors():
    pass


def test_game_viewset_update_success():
    pass


def test_game_viewset_update_errors():
    pass


def test_game_viewset_destroy_success():
    pass


def test_game_viewset_destroy_errors():
    pass
