import pytest
from model_bakery import baker

from core.models import User


@pytest.fixture
@pytest.mark.django_db
def user_fixture():
    return baker.make(User)


@pytest.mark.django_db
def test_user_str(user_fixture):
    assert str(user_fixture) == user_fixture.username
