import pytest
from tests.fixtures.fixture_object import (
    fixture_nested_obj, fixture_bad_type_in_nested_obj,
    fixture_enum_obj, fixture_enum_obj_not_in_choice)
from tests.fixtures.fixture_models import (
    fixture_schema_test_model, fixture_nested_schema,
    fixture_pmodel, fixture_swagger_test_model,
    fixture_user_model, fixture_enum_schema,
    fixture_enum_schema_set, fixture_enum_schema_tuple,
    fixture_bad_enum_schema, fixture_bad_enum_schema_type)


# Schemas
@pytest.fixture
def schema_test_model():
    return fixture_schema_test_model()


@pytest.fixture
def nested_schema():
    return fixture_nested_schema()


@pytest.fixture
def pmodel():
    return fixture_pmodel()


@pytest.fixture
def swagger_test_model():
    return fixture_swagger_test_model()


@pytest.fixture
def user_model():
    return fixture_user_model()


@pytest.fixture
def enum_schema():
    return fixture_enum_schema()


@pytest.fixture
def enum_schema_set():
    return fixture_enum_schema_set()


@pytest.fixture
def enum_schema_tuple():
    return fixture_enum_schema_tuple()


@pytest.fixture
def bad_enum_schema():
    return fixture_bad_enum_schema()


@pytest.fixture
def bad_enum_schema_type():
    return fixture_bad_enum_schema_type()


# Objects
@pytest.fixture
def nested_obj():
    return fixture_nested_obj()


@pytest.fixture
def bad_type_in_nested_obj():
    return fixture_bad_type_in_nested_obj()


@pytest.fixture
def enum_obj():
    return fixture_enum_obj()


@pytest.fixture
def enum_obj_not_in_choice():
    return fixture_enum_obj_not_in_choice()