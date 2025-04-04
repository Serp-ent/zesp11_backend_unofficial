import pytest
from django.contrib.auth.models import User
from gotale.models import Location, Session, Game, Choice, Step, Scenario
from rest_framework.test import APIClient


@pytest.fixture
@pytest.mark.django_db
def user1():
    return User.objects.create_user(
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
        name="Test Location", latitude=10.0, longitude=20.0
    )

    # Create a scenario authored by user1
    scenario = Scenario.objects.create(name="Test Scenario", author=user1)
    step1 = Step.objects.create(
        title="Step 1", text="First step", scenario=scenario, location=location
    )
    step2 = Step.objects.create(
        title="Step 2", text="Second step", scenario=scenario, location=location
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
