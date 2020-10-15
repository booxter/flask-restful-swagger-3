import pytest
from tests.fixtures.fixture_models import fixture_nested_obj, fixture_bad_type_in_nested_obj


@pytest.fixture
def nested_obj():
    return fixture_nested_obj()


@pytest.fixture
def bad_type_in_nested_obj():
    return fixture_bad_type_in_nested_obj()
