"""This script is for manual testing"""

import random

from django.contrib.auth import get_user_model

from gotale.models import (
    Choice,
    Game,
    History,
    Location,
    Scenario,
    Session,
    Step,
)

User = get_user_model()

# Create Superuser for Testing (if not exists)
user, created = User.objects.get_or_create(
    username="testuser", defaults={"password": "password"}
)
print(f"User: {user.username} {'(created)' if created else '(exists)'}")

# Create Locations
locations = [
    {"name": "New York", "latitude": 40.712776, "longitude": -74.005974},
    {"name": "London", "latitude": 51.507351, "longitude": -0.127758},
    {"name": "Tokyo", "latitude": 35.689487, "longitude": 139.691711},
    {"name": "Sydney", "latitude": -33.868820, "longitude": 151.209290},
]

location_objs = [Location.objects.get_or_create(**loc)[0] for loc in locations]
print("✅ Locations added.")

# Create Scenario
scenario = Scenario.objects.create(
    name="Adventure Quest", author=user, root_step_id=None
)
print(f"✅ Scenario '{scenario.name}' created.")

# Create Steps
step1 = Step.objects.create(
    title="Start",
    text="Welcome to the adventure!",
    scenario=scenario,
    location=random.choice(location_objs),
)
step2 = Step.objects.create(
    title="Forest",
    text="You enter a dark forest.",
    scenario=scenario,
    location=random.choice(location_objs),
)
step3 = Step.objects.create(
    title="Cave",
    text="You find a hidden cave.",
    scenario=scenario,
    location=random.choice(location_objs),
)
step4 = Step.objects.create(
    title="Castle",
    text="A castle appears in the distance.",
    scenario=scenario,
    location=random.choice(location_objs),
)

# Assign Root Step
scenario.root_step = step1
scenario.save()
print(f"✅ Root step assigned: {scenario.root_step.title}")

# Create Choices
Choice.objects.create(step=step1, text="Go to the forest", next=step2)
Choice.objects.create(step=step1, text="Go to the cave", next=step3)
Choice.objects.create(step=step2, text="Go to the castle", next=step4)
Choice.objects.create(step=step3, text="Return to the start", next=step1)

print("✅ Choices created.")

# Create a Game
game = Game.objects.create(user=user, scenario=scenario, current_step=step1)
print(f"✅ Game started: {game}")

# Create a Session
session = Session.objects.create(game=game)
print(f"✅ Session started for game {game.id}")

# Create History
History.objects.create(session=session, choice=Choice.objects.first(), step=step1)
print("✅ History recorded.")

print("\n🎉 Database populated successfully!")
