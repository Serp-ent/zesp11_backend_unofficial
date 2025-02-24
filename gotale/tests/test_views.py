import pytest
from django.urls import reverse


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
