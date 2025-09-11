from unittest.mock import ANY

import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from gotale.models import Location
from tests.core.test_user_viewset import USER_LIST

LOCATION_LIST = [
    {
        "id": "4e798487-e8b8-41bf-a49a-000000000000",
        "description": None,
        "latitude": "1.000000",
        "longitude": "1.000000",
        "title": "Location 1",
        "created_by": USER_LIST[0],
        "created_at": ANY,
        "modified_by": None,
        "modified_at": ANY,
    },
    {
        "id": "4e798487-e8b8-41bf-a49a-000000000001",
        "description": "Description for Location 2",
        "latitude": "2.000000",
        "longitude": "2.000000",
        "title": "Location 2",
        "created_by": USER_LIST[0],
        "created_at": ANY,
        "modified_by": None,
        "modified_at": ANY,
    },
    {
        "id": "4e798487-e8b8-41bf-a49a-000000000002",
        "description": None,
        "latitude": "3.000000",
        "longitude": "3.000000",
        "title": "Location 3",
        "created_by": USER_LIST[0],
        "created_at": ANY,
        "modified_by": None,
        "modified_at": ANY,
    },
]


@pytest.fixture
def locations_fixture(users_fixture):
    return Location.objects.bulk_create(
        [
            baker.prepare(
                Location,
                id="4e798487-e8b8-41bf-a49a-000000000000",
                title="Location 1",
                created_by=users_fixture[0],
                latitude=1.0,
                longitude=1.0,
            ),
            baker.prepare(
                Location,
                id="4e798487-e8b8-41bf-a49a-000000000001",
                title="Location 2",
                created_by=users_fixture[0],
                latitude=2.0,
                longitude=2.0,
                description="Description for Location 2",
            ),
            baker.prepare(
                Location,
                id="4e798487-e8b8-41bf-a49a-000000000002",
                title="Location 3",
                created_by=users_fixture[0],
                latitude=3.0,
                longitude=3.0,
            ),
        ]
    )


# TOD
# @pytest.mark.django_db
# @pytest.mark.parametrize(
#     "url, method, url_args, expected_status_code",
#     [
#         pytest.param(
#             "list",
#             "get",
#             {},
#             status.HTTP_200_OK,
#             id="list",
#         ),
#         pytest.param(
#             "list",
#             "post",
#             {},
#             status.HTTP_403_FORBIDDEN,
#             id="create",
#         ),
#         pytest.param(
#             "detail",
#             "get",
#             {"pk": "4e798487-e8b8-41bf-a49a-000000000000"},
#             status.HTTP_200_OK,
#             id="retrieve",
#         ),
#         pytest.param(
#             "detail",
#             "put",
#             {"pk": "4e798487-e8b8-41bf-a49a-000000000000"},
#             status.HTTP_403_FORBIDDEN,
#             id="update",
#         ),
#         pytest.param(
#             "detail",
#             "patch",
#             {"pk": "4e798487-e8b8-41bf-a49a-000000000000"},
#             status.HTTP_403_FORBIDDEN,
#             id="partial_update",
#         ),
#         pytest.param(
#             "detail",
#             "delete",
#             {"pk": "4e798487-e8b8-41bf-a49a-000000000000"},
#             status.HTTP_403_FORBIDDEN,
#             id="destroy",
#         ),
#     ],
# )
# def test_locations_viewset_permissions_anon(
#     # TODO: only admin can create/update/delete
#     anon_client,
#     locations_fixture,
#     url,
#     method,
#     url_args,
#     expected_status_code,
# ):
#     url = reverse(f"location-{url}", kwargs=url_args)
#     response = getattr(anon_client, method)(url)

#     assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_locations_viewset_list(anon_client, locations_fixture):
    url = reverse("location-list")
    response = anon_client.get(url)

    assert (response.status_code, response.json()) == (
        status.HTTP_200_OK,
        LOCATION_LIST,
    )


@pytest.mark.django_db
def test_locations_viewset_retrieve_success(anon_client, locations_fixture):
    response = anon_client.get(
        reverse("location-detail", kwargs={"pk": locations_fixture[0].pk})
    )

    assert (response.status_code, response.json()) == (
        status.HTTP_200_OK,
        LOCATION_LIST[0],
    )


@pytest.mark.django_db
def test_locations_viewset_retrieve_errors(
    anon_client,
    locations_fixture,
):
    response = anon_client.get(reverse("location-detail", kwargs={"pk": 9999}))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "data",
    (
        pytest.param(
            {
                "title": "New Location",
                "latitude": "1.000000",
                "longitude": "1.000000",
                "description": "Description for New Location",
            },
            id="with_description",
        ),
        pytest.param(
            {
                "title": "New Location",
                "latitude": "1.000000",
                "longitude": "1.000000",
            },
            id="without_description",
        ),
    ),
)
@pytest.mark.django_db
def test_locations_viewset_create_success(auth_client, data):
    response = auth_client.post(reverse("location-list"), data=data)

    assert (response.status_code, response.json()) == (
        status.HTTP_201_CREATED,
        LOCATION_LIST[0]
        | {
            "id": ANY,
        }
        | data,
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "data, exp_status_code, exp_response",
    (
        pytest.param(
            {},
            status.HTTP_400_BAD_REQUEST,
            {
                "latitude": [
                    "This field is required.",
                ],
                "longitude": [
                    "This field is required.",
                ],
                "title": [
                    "This field is required.",
                ],
            },
            id="missing_fields",
        ),
        pytest.param(
            {
                "title": "New Location",
                "latitude": 91.0,
                "longitude": -181.0,
                "description": "Description for New Location",
            },
            status.HTTP_400_BAD_REQUEST,
            {
                "latitude": [
                    "Ensure this value is less than or equal to 90.0.",
                ],
                "longitude": [
                    "Ensure this value is greater than or equal to -180.0.",
                ],
            },
            id="location_out_of_range",
        ),
    ),
)
def test_locations_viewset_create_errors(
    admin_client, data, exp_status_code, exp_response
):
    response = admin_client.post(reverse("location-list"), data=data)
    assert (response.status_code, response.json()) == (exp_status_code, exp_response)


# TODO: put/patch in parametrize
@pytest.mark.django_db
@pytest.mark.parametrize(
    "data",
    (
        pytest.param(
            {
                "latitude": 80.0,
                "longitude": -60.0,
                "description": "Description for New Location",
            },
        ),
    ),
)
def test_locations_viewset_update_success(locations_fixture, auth_client, data):
    response = auth_client.patch(
        reverse("location-detail", kwargs={"pk": locations_fixture[0].id}), data=data
    )
    assert (response.status_code, response.json()) == (
        status.HTTP_200_OK,
        LOCATION_LIST[0]
        | data
        | {
            "id": ANY,
            "latitude": "80.000000",
            "longitude": "-60.000000",
            "title": locations_fixture[0].title,
        },
    )


# TODO use idff enhanced


@pytest.mark.django_db
@pytest.mark.parametrize(
    "data, expected_status_code, expected_response",
    (
        pytest.param(
            {
                "latitude": 91.0,
                "longitude": -181.0,
            },
            status.HTTP_400_BAD_REQUEST,
            {
                "latitude": ["Ensure this value is less than or equal to 90.0."],
                "longitude": ["Ensure this value is greater than or equal to -180.0."],
            },
            id="location_values_out_of_range",
        ),
        pytest.param(
            {
                "title": "",
            },
            status.HTTP_400_BAD_REQUEST,
            {
                "title": ["This field may not be blank."],
            },
            id="empty_title",
        ),
        pytest.param(
            {
                "latitude": "",
                "longitude": "",
            },
            status.HTTP_400_BAD_REQUEST,
            {
                "latitude": ["A valid number is required."],
                "longitude": ["A valid number is required."],
            },
            id="location_values_empty",
        ),
    ),
)
def test_locations_viewset_update_errors(
    locations_fixture, auth_client, data, expected_status_code, expected_response
):
    response = auth_client.patch(
        reverse("location-detail", kwargs={"pk": locations_fixture[0].id}), data=data
    )

    assert (response.status_code, response.json()) == (
        expected_status_code,
        expected_response,
    )


@pytest.mark.django_db
def test_locations_viewset_destroy_success(locations_fixture, admin_client):
    response = admin_client.delete(
        reverse("location-detail", kwargs={"pk": locations_fixture[0].id})
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Location.objects.filter(id=locations_fixture[0].id).exists()


@pytest.mark.parametrize(
    "pk, expected_status_code",
    (
        pytest.param(
            "9999",
            status.HTTP_204_NO_CONTENT,
            id="invalid_pk",
        ),
    ),
)
@pytest.mark.django_db
def test_locations_viewset_destroy_errors(
    locations_fixture, admin_client, pk, expected_status_code
):
    response = admin_client.delete(
        reverse("location-detail", kwargs={"pk": locations_fixture[0].id})
    )
    assert response.status_code == expected_status_code


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
