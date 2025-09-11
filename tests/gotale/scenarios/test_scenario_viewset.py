from unittest.mock import ANY

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from gotale.models import Choice, Scenario, Step
from tests.core.test_user_viewset import USER_LIST
from tests.utils import is_valid_uuid4

User = get_user_model()


SCENARIO_LIST = [
    {
        "created_by": USER_LIST[0],
        "created_at": ANY,
        "modified_by": None,
        "modified_at": ANY,
        "description": "Test Description",
        "id": "01234567-89ab-cdef-0123-000000000000",
        "root_step": {
            "description": None,
            "id": "01234567-89ab-cdef-0123-111111111111",
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
            "location": None,
            "title": "Root Step",
        },
        "title": "Test Scenario",
    },
    {
        "created_at": ANY,
        "created_by": USER_LIST[0],
        "description": "A simple story",
        "id": "c5970ee6-8837-452b-b851-000000000001",
        "modified_at": ANY,
        "modified_by": None,
        "root_step": {
            "choices": [
                {
                    "id": ANY,
                    "text": "Go to 2",
                },
                {
                    "id": ANY,
                    "text": "Go to 3",
                },
            ],
            "description": None,
            "id": ANY,
            "location": None,
            "title": "step 1",
        },
        "title": "Time Travel Adventure",
    },
]

SCENARIO_CREATE_PAYLOAD = {
    "title": "Time Travel Adventure",
    "description": "A simple story",
    "steps": [
        {
            "id": 1,
            "title": "step 1",
            "choices": [
                {"text": "Go to 2", "next": 2},
                {"text": "Go to 3", "next": 3},
            ],
        },
        {
            "id": 2,
            "title": "step 2",
            "choices": [
                {"text": "Go to 4", "next": 4},
                {"text": "Go to 5", "next": 5},
            ],
        },
        {
            "id": 3,
            "title": "step 3",
            "choices": [
                {"text": "Go to 6", "next": 6},
            ],
        },
        {
            "id": 4,
            "title": "step 4",
            "choices": [],
        },
        {
            "id": 5,
            "title": "step 5",
            "choices": [],
        },
        {
            "id": 6,
            "title": "step 6",
            "choices": [],
        },
    ],
}


# @pytest.mark.django_db
# def test_scenario_viewset_list_success(anon_client, user1):
#     Scenario.objects.create(title="Test Scenario", author=user1)
#     url = reverse("scenario-list")
#     response = anon_client.get(url)
#     assert response.status_code == status.HTTP_200_OK
#     assert len(response.data) > 0


@pytest.mark.django_db
def test_scenario_viewset_retrieve_success(
    scenario_fixture, anon_client, users_fixture
):
    response = anon_client.get(
        reverse("scenario-detail", kwargs={"pk": scenario_fixture.pk})
    )

    assert (response.status_code, response.json()) == (
        status.HTTP_200_OK,
        SCENARIO_LIST[0],
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "pk",
    [
        pytest.param("01234567-89ab-cdef-0123-000000000001", id="not_found"),
    ],
)
def test_scenario_viewset_retrieve_errors(anon_client, scenario_fixture, pk):
    response = anon_client.get(reverse("scenario-detail", kwargs={"pk": pk}))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_scenario_viewset_create_success(auth_client):
    response = auth_client.post(
        reverse("scenario-list"),
        data=SCENARIO_CREATE_PAYLOAD,
        format="json",
    )

    assert (response.status_code, response.json()) == (
        status.HTTP_201_CREATED,
        SCENARIO_LIST[1] | {"id": ANY},
    )

    response_json = response.json()
    assert Scenario.objects.filter(pk=response_json["id"]).exists()
    assert list(
        Scenario.objects.get(pk=response_json["id"]).root_step.choices.values(
            "id", "text"
        )
    ) == [
        {
            "id": ANY,
            "text": "Go to 2",
        },
        {
            "id": ANY,
            "text": "Go to 3",
        },
    ]

    # Check if the steps ids are correctly changed to UUID from the Frontend
    assert all(
        [
            is_valid_uuid4(str(id))
            for id in Step.objects.filter(scenario=response_json["id"]).values_list(
                "id", flat=True
            )
        ]
    )


@pytest.mark.parametrize(
    "payload, expected_status_code, expected_response_data",
    (
        pytest.param(
            {
                "title": "Time Travel Adventure",
                "description": "A simple story",
                "steps": [],
            },
            status.HTTP_400_BAD_REQUEST,
            {
                "steps": [
                    "A scenario must have at least one step.",
                ],
            },
            id="empty_steps",
        ),
        pytest.param(
            {
                "title": "Time Travel Adventure",
                "description": "A simple story",
                "steps": [
                    {
                        "id": 1,
                        "title": "step 1",
                        "description": "",
                        "location": "",
                        "choices": [
                            {"text": "Go to 2", "next": 2},
                        ],
                    },
                ],
            },
            status.HTTP_400_BAD_REQUEST,
            {
                "steps": [
                    "Step 1 has a choice pointing to non-existent step {'text': 'Go to 2', 'next': 2}.",
                ],
            },
            id="choices_point_to_unknown_steps",
        ),
        pytest.param(
            {
                "title": "Time Travel Adventure",
                "description": "A simple story",
                "steps": [
                    {
                        "id": 1,
                        "title": "step 1",
                        "description": "",
                        "location": "",
                        "choices": [
                            {"text": "Go to 1", "next": 2},
                            {"text": "Go to 2", "next": 2},
                            {"text": "Go to 3", "next": 2},
                            {"text": "Go to 4", "next": 2},
                            {"text": "Go to 5", "next": 2},
                        ],
                    },
                    {
                        "id": 2,
                        "title": "step 1",
                        "description": "",
                        "location": "",
                        "choices": [],
                    },
                ],
            },
            status.HTTP_400_BAD_REQUEST,
            {
                "steps": [
                    "Step 1 has more than 4 choices. A step cannot have more than 4 choices.",
                ],
            },
            id="more_than_4_choices",
        ),
        pytest.param(
            {
                "title": "Time Travel Adventure",
                "description": "A simple story",
                "steps": [
                    {
                        "id": 1,
                        "title": "step 1",
                        "choices": [
                            {"text": "Go to 2", "next": 2},
                            {"text": "Go to 2", "next": 2},
                        ],
                    },
                    {
                        "id": 2,
                        "title": "step 2",
                        "choices": [],
                    },
                    {
                        "id": 2,
                        "title": "step 3",
                        "choices": [],
                    },
                ],
            },
            status.HTTP_400_BAD_REQUEST,
            {
                "steps": [
                    "Step with id 2 is duplicated.",
                ],
            },
            id="step_with_same_id",
        ),
        pytest.param(
            {
                "title": "Time Travel Adventure",
                "description": "A simple story",
                "steps": [
                    {
                        "id": 1,
                        "title": "step 1",
                        "description": "",
                        "location": "",
                        "choices": [],
                    },
                    {
                        "id": 2,
                        "title": "step 1",
                        "description": "",
                        "location": "",
                        "choices": [],
                    },
                ],
            },
            status.HTTP_400_BAD_REQUEST,
            {
                "steps": [
                    "Multiple root steps found: [1, 2]. There must be exactly one root step.",
                ],
            },
            id="two_root_steps",
        ),
    ),
)
@pytest.mark.django_db
def test_scenario_viewset_create_errors(
    auth_client, expected_status_code, expected_response_data, payload
):
    response = auth_client.post(
        reverse("scenario-list"),
        data=payload,
        format="json",
    )

    assert (response.status_code, response.json()) == (
        expected_status_code,
        expected_response_data,
    )


def test_scenario_viewset_update_success():
    # TODO: replace whole scenario
    pass


def test_scenario_viewset_update_errors():
    # TODO:
    pass


@pytest.mark.django_db
def test_scenario_viewset_destroy_success(admin_client, scenario_fixture):
    steps = Scenario.objects.get(pk=scenario_fixture.id).steps.all()

    response = admin_client.delete(
        reverse("scenario-detail", kwargs={"pk": scenario_fixture.id})
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Scenario.objects.filter(pk=scenario_fixture.id).exists()
    assert not Step.objects.filter(scenario=scenario_fixture.id).exists()
    assert not Choice.objects.filter(step__in=steps).exists()


@pytest.mark.parametrize(
    "pk, expected_status_code",
    (
        pytest.param(
            "1232131",
            status.HTTP_404_NOT_FOUND,
        ),
    ),
)
@pytest.mark.django_db
def test_scenario_viewset_destroy_errors(
    admin_client, scenario_fixture, pk, expected_status_code
):
    response = admin_client.delete(reverse("scenario-detail", kwargs={"pk": pk}))

    assert response.status_code == expected_status_code
