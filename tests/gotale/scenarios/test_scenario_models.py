import pytest


@pytest.mark.django_db
def test_scenario_str(scenario_fixture):
    assert str(scenario_fixture) == scenario_fixture.title


@pytest.mark.django_db
def test_step_str(scenario_fixture):
    step = scenario_fixture.root_step

    assert str(step) == f"{scenario_fixture.title} - {step.title}"


@pytest.mark.django_db
def test_choice_str(scenario_fixture):
    choice = scenario_fixture.root_step.choices.all()[0]

    assert str(choice) == choice.text
