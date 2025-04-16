import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from backend.gotale.models import Location

LOCATION_LIST = [
    {
        "description": None,
        "latitude": "1.000000",
        "longitude": "1.000000",
        "title": "Location 1",
    },
    {
        "description": "Description for Location 2",
        "latitude": "2.000000",
        "longitude": "2.000000",
        "title": "Location 2",
    },
    {
        "description": None,
        "latitude": "3.000000",
        "longitude": "3.000000",
        "title": "Location 3",
    },
]


@pytest.fixture
def locations_fixture():
    Location.objects.bulk_create(
        [
            baker.prepare(Location, title="Location 1", latitude=1.0, longitude=1.0),
            baker.prepare(
                Location,
                title="Location 2",
                latitude=2.0,
                longitude=2.0,
                description="Description for Location 2",
            ),
            baker.prepare(
                Location,
                title="Location 3",
                latitude=3.0,
                longitude=3.0,
            ),
        ]
    )


@pytest.mark.django_db
def test_locations_viewset_list(anon_client, locations_fixture):
    url = reverse("location-list")
    response = anon_client.get(url)

    assert (response.status_code, response.json()) == (
        status.HTTP_200_OK,
        LOCATION_LIST,
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "action, method, url_args",
    [
        pytest.param("list", "get", {}, id="list"),
        # pytest.param("create", "post"),
        pytest.param("detail", "get", {"pk": 1}, id="retrieve"),
        # pytest.param("destroy", "delete"),
        # pytest.param("update", "put"),
        # pytest.param("partial-update", "patch"),
    ],
)
def test_locations_viewset_anon_permissions(
    anon_client,
    locations_fixture,
    action,
    method,
    url_args,
):
    url = reverse(f"location-{action}", kwargs=url_args)
    response = getattr(anon_client, method)(url)

    assert response.status_code == status.HTTP_200_OK


def test_locations_viewset_list_success():
    pass


def test_locations_viewset_retrieve_success():
    pass


def test_locations_viewset_retrieve_errors():
    pass


def test_locations_viewset_create_success():
    pass


def test_locations_viewset_create_errors():
    pass


def test_locations_viewset_update_success():
    pass


def test_locations_viewset_update_errors():
    pass


def test_locations_viewset_destroy_success():
    pass


def test_locations_viewset_destroy_errors():
    pass


# @pytest.mark.django_db
# def test_anon_cannot_create_location(anon_client):
#     url = reverse("location-list")
#     data = {"title": "New Location", "latitude": 0.0, "longitude": 0.0}
#     response = anon_client.post(url, data)
#     assert response.status_code == status.HTTP_403_FORBIDDEN


# @pytest.mark.django_db
# def test_auth_nonadmin_cannot_create_location(auth_client1):
#     url = reverse("location-list")
#     data = {"name": "New Location", "latitude": 0.0, "longitude": 0.0}
#     response = auth_client1.post(url, data)
#     assert response.status_code == status.HTTP_403_FORBIDDEN


# @pytest.mark.django_db
# def test_admin_can_create_location(admin_client):
#     url = reverse("location-list")
#     data = {"title": "New Location", "latitude": 0.0, "longitude": 0.0}
#     response = admin_client.post(url, data)
#     assert response.status_code == status.HTTP_201_CREATED
#     assert Location.objects.filter(title="New Location").exists()


# # Tests for detail (retrieve/update/delete) actions
# # -------------------------------------------------


# @pytest.mark.django_db
# def test_anon_can_retrieve_location(anon_client):
#     location = Location.objects.create(
#         title="Test Location", latitude=0.0, longitude=0.0
#     )
#     url = reverse("location-detail", kwargs={"pk": location.pk})
#     response = anon_client.get(url)
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data["title"] == "Test Location"


# @pytest.mark.django_db
# def test_auth_nonadmin_cannot_update_location(auth_client1):
#     location = Location.objects.create(
#         title="Test Location", latitude=0.0, longitude=0.0
#     )
#     url = reverse("location-detail", kwargs={"pk": location.pk})
#     data = {"title": "Updated Name"}
#     response = auth_client1.patch(url, data)
#     assert response.status_code == status.HTTP_403_FORBIDDEN


# @pytest.mark.django_db
# def test_admin_can_update_location(admin_client):
#     location = Location.objects.create(
#         title="Test Location", latitude=0.0, longitude=0.0
#     )
#     url = reverse("location-detail", kwargs={"pk": location.pk})
#     data = {"title": "Updated Name"}
#     response = admin_client.patch(url, data)
#     assert response.status_code == status.HTTP_200_OK
#     location.refresh_from_db()
#     assert location.title == "Updated Name"


# @pytest.mark.django_db
# def test_admin_can_delete_location(admin_client):
#     location = Location.objects.create(
#         title="Test Location", latitude=0.0, longitude=0.0
#     )
#     url = reverse("location-detail", kwargs={"pk": location.pk})
#     response = admin_client.delete(url)
#     assert response.status_code == status.HTTP_204_NO_CONTENT
#     assert not Location.objects.filter(pk=location.pk).exists()


# @pytest.mark.django_db
# def test_auth_nonadmin_cannot_delete_location(auth_client1):
#     location = Location.objects.create(
#         title="Test Location", latitude=0.0, longitude=0.0
#     )
#     url = reverse("location-detail", kwargs={"pk": location.pk})
#     response = auth_client1.delete(url)
#     assert response.status_code == status.HTTP_403_FORBIDDEN
