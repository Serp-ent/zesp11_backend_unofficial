import pytest
from django.urls import reverse
from rest_framework import status
from gotale.models import Location, Scenario


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
    data = {
        "name": "New Location",
        "latitude": 0.0,
        "longitude": 0.0
    }
    response = anon_client.post(url, data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_auth_nonadmin_cannot_create_location(auth_client1):
    url = reverse("location-list")
    data = {
        "name": "New Location",
        "latitude": 0.0,
        "longitude": 0.0
    }
    response = auth_client1.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_create_location(admin_client):
    url = reverse("location-list")
    data = {
        "name": "New Location",
        "latitude": 0.0,
        "longitude": 0.0
    }
    response = admin_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Location.objects.filter(name="New Location").exists()


# Tests for detail (retrieve/update/delete) actions
# -------------------------------------------------

@pytest.mark.django_db
def test_anon_can_retrieve_location(anon_client):
    location = Location.objects.create(
        name="Test Location", 
        latitude=0.0, 
        longitude=0.0
    )
    url = reverse("location-detail", kwargs={"pk": location.pk})
    response = anon_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Test Location"


@pytest.mark.django_db
def test_auth_nonadmin_cannot_update_location(auth_client1):
    location = Location.objects.create(
        name="Test Location", 
        latitude=0.0, 
        longitude=0.0
    )
    url = reverse("location-detail", kwargs={"pk": location.pk})
    data = {"name": "Updated Name"}
    response = auth_client1.patch(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_update_location(admin_client):
    location = Location.objects.create(
        name="Test Location", 
        latitude=0.0, 
        longitude=0.0
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
        name="Test Location", 
        latitude=0.0, 
        longitude=0.0
    )
    url = reverse("location-detail", kwargs={"pk": location.pk})
    response = admin_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Location.objects.filter(pk=location.pk).exists()


@pytest.mark.django_db
def test_auth_nonadmin_cannot_delete_location(auth_client1):
    location = Location.objects.create(
        name="Test Location", 
        latitude=0.0, 
        longitude=0.0
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
