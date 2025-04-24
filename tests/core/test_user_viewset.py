from unittest.mock import ANY

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

User = get_user_model()

USER_LIST = [
    {
        "email": "andrzej@example.com",
        "first_name": "Andrzej",
        "id": "01234567-89ab-cdef-0123-000000000003",
        "last_name": "Kowalski",
        "username": "andrzejkowalski",
        "created": ANY,
        "modified": ANY,
    },
    {
        "email": "marek@example.com",
        "first_name": "Marek",
        "id": "01234567-89ab-cdef-0123-000000000002",
        "last_name": "Pieczarek",
        "username": "marekpieczarek",
        "created": ANY,
        "modified": ANY,
    },
    {
        "email": "jacek@example.com",
        "first_name": "Jacek",
        "id": "01234567-89ab-cdef-0123-000000000001",
        "last_name": "Placek",
        "username": "jacekplacek",
        "created": ANY,
        "modified": ANY,
    },
]


@pytest.mark.django_db
def test_user_viewset_create_success(anon_client):
    body = {
        "username": "marekpieczarek",
        "password": "password123",
        "email": "marek@pieczarek.com",
    }
    response = anon_client.post(reverse("register"), data=body)

    assert (response.status_code, response.json()) == (
        status.HTTP_201_CREATED,
        {
            "created": ANY,
            "modified": ANY,
            "email": "marek@pieczarek.com",
            "first_name": "",
            "id": ANY,
            "last_name": "",
            "username": "marekpieczarek",
        },
    )


# TODO: enable password validation
@pytest.mark.parametrize(
    "body, response_body",
    [
        pytest.param(
            {
                "username": "",
                "password": "",
                "email": "",
            },
            {
                "username": ["This field may not be blank."],
                "email": ["This field may not be blank."],
                "password": ["This field may not be blank."],
            },
            id="missing_fields",
        ),
        pytest.param(
            {
                "username": "marekpieczarek",
                "password": "password123",
                "email": "marek",
            },
            {
                "email": ["Enter a valid email address."],
            },
            id="invalid_email",
        ),
    ],
)
@pytest.mark.django_db
def test_user_viewset_create_errors(anon_client, body, response_body):
    response = anon_client.post(reverse("register"), data=body)

    assert (response.status_code, response.json()) == (
        status.HTTP_400_BAD_REQUEST,
        response_body,
    )


@pytest.mark.django_db
def test_user_viewset_retrieve_success(anon_client, users_fixture):
    response = anon_client.get(
        reverse("user-detail", kwargs={"pk": USER_LIST[2]["id"]})
    )

    assert (response.status_code, response.json()) == (status.HTTP_200_OK, USER_LIST[2])


@pytest.mark.django_db
def test_user_viewset_retrieve_errors(anon_client):
    response = anon_client.get(
        reverse("user-detail", kwargs={"pk": "01234567-89ab-cdef-0123-000000000001"})
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_user_viewset_list_success(anon_client, users_fixture):
    response = anon_client.get(reverse("user-list"))

    assert (response.status_code, response.json()) == (status.HTTP_200_OK, USER_LIST)


@pytest.mark.django_db
# TODO: updating password
def test_user_viewset_update_success(auth_client, users_fixture):
    data = {
        "first_name": "Andrzej",
    }
    response = auth_client.patch(
        reverse("user-detail", kwargs={"pk": USER_LIST[0]["id"]}),
    )

    assert (response.status_code, response.json()) == (
        status.HTTP_200_OK,
        USER_LIST[0] | data,
    )


@pytest.mark.parametrize(
    "body, expected_status_code, expected_response_body",
    (
        pytest.param(
            {
                "username": "",
                "password": "",
                "email": "",
            },
            status.HTTP_400_BAD_REQUEST,
            {
                "email": [
                    "This field may not be blank.",
                ],
                "username": [
                    "This field may not be blank.",
                ],
                "password": [
                    "This field may not be blank.",
                ],
            },
            id="missing_fields",
        ),
        pytest.param(
            {
                "username": "marekpieczarek",
                "email": "marek@example.com",
            },
            status.HTTP_400_BAD_REQUEST,
            {
                "email": [
                    "user with this email already exists.",
                ],
                "username": [
                    "A user with that username already exists.",
                ],
            },
            id="fields_already_used",
        ),
    ),
)
@pytest.mark.django_db
def test_user_viewset_update_errors(
    auth_client, users_fixture, body, expected_status_code, expected_response_body
):
    response = auth_client.patch(
        reverse("user-detail", kwargs={"pk": USER_LIST[0]["id"]}),
        data=body,
    )

    assert (response.status_code, response.json()) == (
        expected_status_code,
        expected_response_body,
    )


# @pytest.mark.django_db
# def test_user_viewset_delete_errors(anon_client, users_fixture):
#     # TODO: account deactivation
#     anon_client.force_authenticate(user=users_fixture[0])
#     response = anon_client.delete(
#         reverse("user-detail", kwargs={"pk": users_fixture[0].id})
#     )
#     assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


# cannot delete user account
# Only owner/admin can update their account
