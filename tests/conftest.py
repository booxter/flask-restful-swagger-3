import pytest
from tests.fixtures import fixture_object, fixture_models, fixture_resources, fixture_swagger


# Resources
@pytest.fixture
def user_resource():
    return fixture_resources.user_resource()


@pytest.fixture
def entity_add_resource():
    return fixture_resources.entity_add_resource()


@pytest.fixture
def parse_resource():
    return fixture_resources.parse_resource()


@pytest.fixture
def bad_format_resource():
    return fixture_resources.bad_format_resource()


@pytest.fixture
def one_resource():
    return fixture_resources.one_resource()


@pytest.fixture
def p_resource():
    return fixture_resources.p_resource()


@pytest.fixture
def bad_format_url():
    return fixture_resources.bad_format_url()


@pytest.fixture
def no_converter_resource():
    return fixture_resources.no_converter_resource()


@pytest.fixture
def bad_schema_resource_in_parameters():
    return fixture_resources.bad_schema_resource_in_parameters()


# Schemas
@pytest.fixture
def schema_test_model():
    return fixture_models.schema_test_model()


@pytest.fixture
def nested_schema():
    return fixture_models.nested_schema()


@pytest.fixture
def p_model():
    return fixture_models.p_model()


@pytest.fixture
def swagger_test_model():
    return fixture_models.swagger_test_model()


@pytest.fixture
def user_model():
    return fixture_models.user_model()


@pytest.fixture
def enum_schema():
    return fixture_models.enum_schema()


@pytest.fixture
def enum_schema_set():
    return fixture_models.enum_schema_set()


@pytest.fixture
def enum_schema_tuple():
    return fixture_models.enum_schema_tuple()


@pytest.fixture
def bad_enum_schema():
    return fixture_models.bad_enum_schema()


@pytest.fixture
def bad_enum_schema_type():
    return fixture_models.bad_enum_schema_type()


@pytest.fixture
def sub_schema():
    return fixture_models.sub_schema()


@pytest.fixture
def sub_schema_without_required():
    return fixture_models.sub_schema_without_required()


@pytest.fixture
def sub_schema_empty():
    return fixture_models.sub_schema_empty()


@pytest.fixture
def bad_sub_schema():
    return fixture_models.bad_sub_schema


@pytest.fixture
def sub_schema_with_bad_super_schema():
    return fixture_models.sub_schema_with_bad_super_schema


@pytest.fixture
def sub_schema_with_super_schema_without_type():
    return fixture_models.sub_schema_with_super_schema_without_type


@pytest.fixture
def schema_with_array():
    return fixture_models.schema_with_array()


@pytest.fixture
def nullable_schema():
    return fixture_models.nullable_schema()


@pytest.fixture
def bad_nullable_schema():
    return fixture_models.bad_nullable_schema()


# Objects
@pytest.fixture
def nested_obj():
    return fixture_object.nested_obj()


@pytest.fixture
def bad_type_in_nested_obj():
    return fixture_object.bad_type_in_nested_obj()


@pytest.fixture
def enum_obj():
    return fixture_object.enum_obj()


@pytest.fixture
def enum_obj_not_in_choice():
    return fixture_object.enum_obj_not_in_choice()


@pytest.fixture
def obj_of_sub_schema():
    return fixture_object.obj_of_sub_schema()


@pytest.fixture
def object_with_array():
    return fixture_object.object_with_array()


# Definitions
@pytest.fixture
def expected_definition_of_sub_schema():
    return fixture_object.expected_definition_of_sub_schema()


# Examples
@pytest.fixture
def expected_example_of_sub_schema():
    return fixture_object.expected_example_of_sub_schema()


# Swagger
@pytest.fixture
def operation_object():
    return fixture_swagger.operation_object()


@pytest.fixture
def parameter_object():
    return fixture_swagger.parameter_object()


@pytest.fixture
def responses_object():
    return fixture_swagger.responses_object()


@pytest.fixture
def request_body():
    return fixture_swagger.request_body()


@pytest.fixture
def components_schemas_object():
    return fixture_swagger.components_schemas_object()


@pytest.fixture
def components_responses_object():
    return fixture_swagger.components_responses_object()


@pytest.fixture
def components_parameters_object():
    return fixture_swagger.components_parameters_object()


@pytest.fixture
def components_examples_object():
    return fixture_swagger.components_examples_object()


@pytest.fixture
def components_request_bodies_object():
    return fixture_swagger.components_request_bodies_object()


@pytest.fixture
def components_headers_object():
    return fixture_swagger.components_headers_object()


@pytest.fixture
def components_security_schemes_object():
    return fixture_swagger.components_security_schemes_object()


@pytest.fixture
def components_link_object():
    return fixture_swagger.components_link_object()


@pytest.fixture
def server_object():
    return fixture_swagger.server_object()
