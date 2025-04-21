import pytest
from model_bakery import baker

from core.models import User
from gotale.models import Choice, Scenario, Step


@pytest.fixture
@pytest.mark.django_db
def user1():
    return baker.make(User, username="user1", password="password1")


@pytest.fixture
@pytest.mark.django_db
def scenario_fixture(user1):
    scenario = baker.make(
        Scenario,
        id="01234567-89ab-cdef-0123-000000000000",
        author=user1,
        title="Test Scenario",
        description="Test Description",
        root_step=None,
    )

    root_step = baker.make(
        Step,
        id="01234567-89ab-cdef-0123-111111111111",
        scenario=scenario,
        title="Root Step",
    )
    scenario.root_step = root_step
    scenario.save()

    child_steps = baker.make(
        Step,
        scenario=scenario,
        _quantity=2,
    )

    choice_data = [
        {
            "id": "01234567-89ab-cdef-0123-000000000011",
            "text": "Go to child 1",
            "next": child_steps[0],
        },
        {
            "id": "01234567-89ab-cdef-0123-000000000022",
            "text": "Go to child 2",
            "next": child_steps[1],
        },
    ]

    [
        baker.make(
            Choice,
            step=root_step,
            id=data["id"],
            text=data["text"],
            next=data["next"],
        )
        for data in choice_data
    ]

    return scenario
