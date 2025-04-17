import pytest
from model_bakery import baker

from backend.gotale.models import Location


@pytest.fixture
def location_fixture():
    return baker.make(Location, title="Nazwa")


@pytest.mark.django_db
def test_location_str(location_fixture):
    assert str(location_fixture) == "Nazwa"
