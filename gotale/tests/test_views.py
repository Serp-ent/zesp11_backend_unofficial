import pytest
from django.urls import reverse
from rest_framework import status
from gotale.models import Location, Scenario, Game, Step, Choice, Session, History
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User


# TODO: group tests by viewset


@pytest.mark.django_db
def test_anon_can_list_user_profiles(anon_client, user1, user2):
    url = reverse("user-list")
    response = anon_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_anon_can_retrieve_user_profile(anon_client, user1):
    # TODO: parametrize
    url = reverse("user-detail", kwargs={"pk": user1.id})
    response = anon_client.get(url)
    assert response.status_code == 200
    assert response.data["username"] == user1.username


@pytest.mark.django_db
def test_auth_can_list_user_profile(auth_client1, user1, user2):
    url = reverse("user-list")
    response = auth_client1.get(url)

    assert response.status_code == 200
    usernames = {u["username"] for u in response.data}
    assert {"user1", "user2"}.issubset(usernames)


@pytest.mark.django_db
def test_auth_can_retrieve_user_profile(auth_client1, user2):
    url = reverse("user-detail", kwargs={"pk": user2.id})
    response = auth_client1.get(url)
    assert response.status_code == 200
    assert response.data["username"] == user2.username


@pytest.mark.django_db
def test_only_admin_can_update_arbitrary_profile(auth_client1, admin_client, user2):
    # TODO: parametrize
    url = reverse("user-detail", kwargs={"pk": user2.id})
    data = {"username": "updated_by_admin"}

    # Non-admin denied
    response = auth_client1.put(url, data)
    assert response.status_code == 403

    # Admin allowed
    response = admin_client.put(url, data)
    assert response.status_code == 200
    user2.refresh_from_db()
    assert user2.username == "updated_by_admin"


@pytest.mark.django_db
def test_only_admin_can_delete_arbitrary_profile(auth_client1, admin_client, user2):
    url = reverse("user-detail", kwargs={"pk": user2.id})

    # Non-admin denied
    response = auth_client1.delete(url)
    assert response.status_code == 403

    # Admin allowed
    response = admin_client.delete(url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_user_can_put_own_profile(auth_client1, user1):
    url = reverse("user-current")
    data = {"username": "new_username", "email": "new@example.com"}

    response = auth_client1.put(url, data)
    assert response.status_code == 200
    user1.refresh_from_db()
    assert user1.username == "new_username"
    assert user1.email == "new@example.com"


@pytest.mark.django_db
def test_user_can_patch_own_profile(auth_client1, user1):
    url = reverse("user-current")
    data = {"email": "patched@example.com"}

    response = auth_client1.patch(url, data)
    assert response.status_code == 200
    user1.refresh_from_db()
    assert user1.email == "patched@example.com"


# Tests for list and create actions
# --------------------------------


@pytest.mark.django_db
def test_anon_can_list_locations(anon_client):
    # Create a test location
    Location.objects.create(name="Test Location", latitude=0.0, longitude=0.0)
    url = reverse("location-list")
    response = anon_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0  # Ensure data is returned


@pytest.mark.django_db
def test_anon_cannot_create_location(anon_client):
    url = reverse("location-list")
    data = {"name": "New Location", "latitude": 0.0, "longitude": 0.0}
    response = anon_client.post(url, data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_auth_nonadmin_cannot_create_location(auth_client1):
    url = reverse("location-list")
    data = {"name": "New Location", "latitude": 0.0, "longitude": 0.0}
    response = auth_client1.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_create_location(admin_client):
    url = reverse("location-list")
    data = {"name": "New Location", "latitude": 0.0, "longitude": 0.0}
    response = admin_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Location.objects.filter(name="New Location").exists()


# Tests for detail (retrieve/update/delete) actions
# -------------------------------------------------


@pytest.mark.django_db
def test_anon_can_retrieve_location(anon_client):
    location = Location.objects.create(
        name="Test Location", latitude=0.0, longitude=0.0
    )
    url = reverse("location-detail", kwargs={"pk": location.pk})
    response = anon_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Test Location"


@pytest.mark.django_db
def test_auth_nonadmin_cannot_update_location(auth_client1):
    location = Location.objects.create(
        name="Test Location", latitude=0.0, longitude=0.0
    )
    url = reverse("location-detail", kwargs={"pk": location.pk})
    data = {"name": "Updated Name"}
    response = auth_client1.patch(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_update_location(admin_client):
    location = Location.objects.create(
        name="Test Location", latitude=0.0, longitude=0.0
    )
    url = reverse("location-detail", kwargs={"pk": location.pk})
    data = {"name": "Updated Name"}
    response = admin_client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    location.refresh_from_db()
    assert location.name == "Updated Name"


@pytest.mark.django_db
def test_admin_can_delete_location(admin_client):
    location = Location.objects.create(
        name="Test Location", latitude=0.0, longitude=0.0
    )
    url = reverse("location-detail", kwargs={"pk": location.pk})
    response = admin_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Location.objects.filter(pk=location.pk).exists()


@pytest.mark.django_db
def test_auth_nonadmin_cannot_delete_location(auth_client1):
    location = Location.objects.create(
        name="Test Location", latitude=0.0, longitude=0.0
    )
    url = reverse("location-detail", kwargs={"pk": location.pk})
    response = auth_client1.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# Tests for list and create actions
# --------------------------------


@pytest.mark.django_db
def test_anon_can_list_scenarios(anon_client, user1):
    Scenario.objects.create(name="Test Scenario", author=user1)
    url = reverse("scenario-list")
    response = anon_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0


@pytest.mark.django_db
def test_anon_cannot_create_scenario(anon_client):
    url = reverse("scenario-list")
    data = {"name": "New Scenario"}

    response = anon_client.post(url, data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not Scenario.objects.filter(name="New Scenario").exists()


# Tests for detail (retrieve/update/delete) actions
# -------------------------------------------------


@pytest.mark.django_db
def test_anon_can_retrieve_scenario(anon_client, user1):
    scenario = Scenario.objects.create(name="Test Scenario", author=user1)
    url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
    response = anon_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Test Scenario"


@pytest.mark.django_db
def test_auth_nonowner_cannot_update_scenario(auth_client1, user2):
    scenario = Scenario.objects.create(name="Test Scenario", author=user2)
    url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
    data = {"name": "Updated Name"}
    response = auth_client1.patch(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_owner_can_update_scenario(auth_client1, user1):
    scenario = Scenario.objects.create(name="Test Scenario", author=user1)
    url = reverse("scenario-detail", kwargs={"pk": scenario.id})
    data = {"name": "Updated Name"}
    response = auth_client1.patch(url, data)
    assert response.status_code == status.HTTP_200_OK

    scenario.refresh_from_db()
    assert scenario.name == "Updated Name"


@pytest.mark.django_db
def test_admin_can_update_scenario(admin_client, user1):
    scenario = Scenario.objects.create(name="Test Scenario", author=user1)
    url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
    data = {"name": "Updated Name"}
    response = admin_client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    scenario.refresh_from_db()
    assert scenario.name == "Updated Name"


@pytest.mark.django_db
def test_owner_can_delete_scenario(auth_client1, user1):
    scenario = Scenario.objects.create(name="Test Scenario", author=user1)
    url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
    response = auth_client1.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Scenario.objects.filter(pk=scenario.pk).exists()


@pytest.mark.django_db
def test_admin_can_delete_scenario(admin_client, user1):
    scenario = Scenario.objects.create(name="Test Scenario", author=user1)
    url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
    response = admin_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Scenario.objects.filter(pk=scenario.pk).exists()


@pytest.mark.django_db
def test_auth_nonowner_cannot_delete_scenario(auth_client1, user2):
    scenario = Scenario.objects.create(name="Test Scenario", author=user2)
    url = reverse("scenario-detail", kwargs={"pk": scenario.pk})
    response = auth_client1.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

# -------------------------------------------------------------

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
        "text": scenario_setup["step1"].text,
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


@pytest.mark.django_db
def test_current_step_post_on_ended_game(auth_client1, create_game, scenario_setup):
    # End the game.
    create_game.end = timezone.now()
    create_game.save()

    url = reverse("game-current-step", args=[create_game.id])
    data = {"choice_id": scenario_setup["choice"].id}
    response = auth_client1.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# # ---------------------------
# # Custom Action: end_session
# # ---------------------------
@pytest.mark.django_db
def test_end_session_in_game_user(auth_client1, create_game):
    url = reverse("game-session-end", args=[create_game.id])
    response = auth_client1.post(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify that the session is now inactive and an end timestamp is set.
    session = create_game.sessions.filter(is_active=False).first()
    assert session is not None, "Session should be deactivated"
    assert session.end is not None


# # ---------------------------
# # Delete Tests
# # ---------------------------
@pytest.mark.django_db
def test_destroy_game_admin(admin_client, create_game):
    url = reverse("game-detail", args=[create_game.id])
    response = admin_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    # The game should be deleted.
    assert not Game.objects.filter(pk=create_game.id).exists()


@pytest.mark.django_db
def test_destroy_game_non_admin(auth_client1, create_game):
    url = reverse("game-detail", args=[create_game.id])
    response = auth_client1.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    # The game should still exist.
    assert Game.objects.filter(pk=create_game.id).exists()

