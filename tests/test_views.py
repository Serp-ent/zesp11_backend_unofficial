import pytest
from django.urls import reverse
from rest_framework import status

from backend.gotale.models import Game


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
