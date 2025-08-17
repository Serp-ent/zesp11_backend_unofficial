from unittest.mock import ANY

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from gotale.models import Choice, Scenario, Step
from tests.core.test_user_viewset import USER_LIST
from tests.utils import is_valid_uuid4

User = get_user_model()

SCENARIOS_LIST = [
    {
        "author": USER_LIST[2],
        "created": ANY,
        "description": "A simple story",
        "id": "09bf5752-190f-4b06-84d6-100000000001",
        "modified": ANY,
        "root_step": None,
        "title": "scenario-title-1",
    },
    {
        "author": USER_LIST[1],
        "created": ANY,
        "description": "A simple story",
        "id": "09bf5752-190f-4b06-84d6-100000000002",
        "modified": ANY,
        "root_step": None,
        "title": "scenario-title-2",
    },
    {
        "author": USER_LIST[0],
        "created": ANY,
        "description": "A simple story",
        "id": "09bf5752-190f-4b06-84d6-100000000003",
        "modified": ANY,
        "root_step": None,
        "title": "scenario-title-3",
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


@pytest.fixture
def scenario_fixtures(users_fixture):
    return Scenario.objects.bulk_create(
        baker.prepare(
            Scenario,
            **(SCENARIO_CREATE_PAYLOAD | {"title": baker.seq("scenario-title-")}),
            id=baker.seq("09bf5752-190f-4b06-84d6-10000000000"),
            author=iter(users_fixture),
            _quantity=3,
        )
    )


@pytest.mark.django_db
def test_scenario_viewset_list_success(anon_client, scenario_fixtures):
    response = anon_client.get(reverse("scenario-list"))
    assert (response.status_code, response.json()) == (
        status.HTTP_200_OK,
        SCENARIOS_LIST,
    )


@pytest.mark.django_db
def test_scenario_viewset_retrieve_success(anon_client, scenario_fixtures):
    response = anon_client.get(
        reverse("scenario-detail", kwargs={"pk": scenario_fixtures[0].pk})
    )

    assert (response.status_code, response.json()) == (
        status.HTTP_200_OK,
        SCENARIOS_LIST[0],
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
        {
            "author": USER_LIST[2],
            "created": ANY,
            "description": "A simple story",
            "id": ANY,
            "modified": ANY,
            "title": "Time Travel Adventure",
            "root_step": {
                "id": ANY,
                "title": "step 1",
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
                "location": ANY,
            },
        },
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
    db_before = tuple(Scenario.objects.all())

    response = auth_client.post(
        reverse("scenario-list"),
        data=payload,
        format="json",
    )

    assert (response.status_code, response.json()) == (
        expected_status_code,
        expected_response_data,
    )
    assert tuple(Scenario.objects.all()) == db_before


@pytest.mark.parametrize("method", ("put", "patch"))
@pytest.mark.django_db
def test_scenario_viewset_update_success(method, auth_client, scenario_fixtures):
    url = reverse("scenario-detail", kwargs={"pk": scenario_fixtures[0].pk})
    response = getattr(auth_client, method)(
        url,
        data={
            "title": "updated-scenario-1-title",
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
                    "choices": [],
                },
                {
                    "id": 3,
                    "title": "step 3",
                    "choices": [],
                },
            ],
        },
    )

    assert (response.status_code, response.json()) == (
        status.HTTP_200_OK,
        SCENARIOS_LIST[0] | {"title": "updated-scenario-1-title"},
    )


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
