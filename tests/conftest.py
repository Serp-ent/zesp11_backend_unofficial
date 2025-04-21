import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework.test import APIClient

from gotale.models import Choice, Game, Location, Scenario, Session, Step

User = get_user_model()


@pytest.fixture
@pytest.mark.django_db
def user1():
    return baker.make(
        User,
        username="user1",
        password="user1",
    )


@pytest.fixture
@pytest.mark.django_db
def user2():
    return User.objects.create_user(
        username="user2",
        password="user2",
    )


@pytest.fixture
@pytest.mark.django_db
def admin_user():
    return User.objects.create_superuser(
        username="admin",
        password="admin",
    )


@pytest.fixture
def anon_client():
    return APIClient()


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def auth_client1(user1):
    client = APIClient()
    client.force_authenticate(user=user1)
    return client


@pytest.fixture
def auth_client2(user2):
    client = APIClient()
    client.force_authenticate(user=user2)
    return client


@pytest.fixture
def scenario_setup(db, user1):
    # Create a location
    location = Location.objects.create(
        title="Test Location", latitude=10.0, longitude=20.0
    )

    # Create a scenario authored by user1
    scenario = Scenario.objects.create(title="Test Scenario", author=user1)
    step1 = Step.objects.create(
        title="Step 1", description="First step", scenario=scenario, location=location
    )
    step2 = Step.objects.create(
        title="Step 2", description="Second step", scenario=scenario, location=location
    )

    # Set the root step if needed
    scenario.root_step = step1
    scenario.save()

    # Create a choice from step1 to step2
    choice = Choice.objects.create(step=step1, text="Advance to step 2", next=step2)

    return {
        "scenario": scenario,
        "step1": step1,
        "step2": step2,
        "choice": choice,
    }


@pytest.fixture
def create_game(db, user1, scenario_setup):
    """
    Create a game owned by user1.
    Manually create an active session with session.user = user1.
    """
    game = Game.objects.create(
        user=user1,
        scenario=scenario_setup["scenario"],
        current_step=scenario_setup["step1"],
    )
    # Simulate auto-created session and assign user
    session = Session.objects.create(game=game, is_active=True)
    session.user = user1
    session.save()
    return game


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
