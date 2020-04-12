import pytest
from flask_restful import inputs
from flask_restful.reqparse import RequestParser

import flask_restful_swagger_3.swagger as swagger

from tests.models import SwaggerTestModel


def test_should_set_nested():
    d = {'openapi': '3.0.0'}
    swagger.set_nested(d, 'info.title', 'API')
    assert d == {'openapi': '3.0.0', 'info': {'title': 'API'}}


def test_should_get_data_type_str():
    assert swagger.get_data_type({'schema': {'type': 'string'}}) == str


def test_should_get_data_type_str_date():
    assert swagger.get_data_type({'schema': {'type': 'string', 'format': 'date'}}) == inputs.date


def test_should_get_data_type_str_date_time():
    assert swagger.get_data_type({'schema': {'type': 'string', 'format': 'date-time'}}) == inputs.datetime_from_iso8601


def test_should_get_data_type_int():
    assert swagger.get_data_type({'schema': {'type': 'integer'}}) == int


def test_should_get_data_type_bool():
    assert swagger.get_data_type({'schema': {'type': 'boolean'}}) == inputs.boolean


def test_should_get_data_type_float():
    assert swagger.get_data_type({'schema': {'type': 'number', 'format': 'float'}}) == float


def test_should_get_data_type_double():
    assert swagger.get_data_type({'schema': {'type': 'number', 'format': 'double'}}) == float


def test_should_get_data_type_invalid():
    assert swagger.get_data_type({}) is None


def test_should_get_data_type_without_type():
    assert swagger.get_data_type({'schema': {}}) is None


def test_should_get_parser_arg():
    param = {
        'name': 'name',
        'description': 'Name to filter by',
        'schema': {
            'type': 'string',
        },
        'in': 'query'
    }

    expected = ('name', {
        'dest': 'name',
        'type': str,
        'location': 'args',
        'help': 'Name to filter by',
        'required': False,
        'default': None,
        'action': 'store'
    })

    assert swagger.get_parser_arg(param) == expected


def test_should_get_parser_args():
    params = [
        {
            'name': 'body',
            'description': 'Request body',
            'in': 'path',
            'required': True,
        },
        {
            'name': 'name',
            'description': 'Name to filter by',
            'schema': {
                'type': 'string'
            },
            'in': 'query'
        }
    ]

    expected = [('name', {
        'dest': 'name',
        'type': str,
        'location': 'args',
        'help': 'Name to filter by',
        'required': False,
        'default': None,
        'action': 'store'
    })]

    assert swagger.get_parser_args(params) == expected


def test_array_get_parser_args():
    params = [
        {
            'name': 'body',
            'description': 'Request body',
            'in': 'path',
            'required': True,
        },
        {
            'name': 'name',
            'description': 'Name to filter by',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'string'
                },
            },
            'in': 'query'
        }
    ]

    expected = [('name', {
        'dest': 'name',
        'type': str,
        'location': 'args',
        'help': 'Name to filter by',
        'required': False,
        'default': None,
        'action': 'append'
    })]

    assert swagger.get_parser_args(params) == expected


def test_should_get_parser():
    params = [{
        'name': 'name',
        'description': 'Name to filter by',
        'schema': {
            'type': 'array',
            'items': {
                'type': 'string'
            },
        },
        'in': 'query'
    }]

    assert swagger.get_parser(params)


def test_should_get_data_action_is_none():
    assert swagger.get_data_action({}) is None


def test_should_validate_info_object_unknown_field():
    info_object = {
        'title': 'test',
        'description': 'my description',
        'version': '0.1',
        'artist': 'Picasso'
    }

    with pytest.raises(swagger.ValidationError):
        assert swagger.validate_info_object(info_object)


def test_should_validate_info_object_missing_title():
    info_object = {
        'description': 'my description',
        'version': '0.1',
    }

    with pytest.raises(swagger.ValidationError):
        assert swagger.validate_info_object(info_object)


def test_should_validate_info_object_missing_version():
    info_object = {
        'title': 'test',
        'description': 'my description',
    }

    with pytest.raises(swagger.ValidationError):
        assert swagger.validate_info_object(info_object)


def test_should_validate_contact_object():
    contact_object = {
        'name': 'John',
        'url': 'test@example.com',
        'email': 'john.doe@example.com'
    }

    assert swagger.validate_contact_object(contact_object) is None


def test_should_validate_contact_object_unknown_field():
    contact_object = {
        'author': 'John'
    }

    with pytest.raises(swagger.ValidationError):
        assert swagger.validate_contact_object(contact_object)


def test_should_validate_license_object():
    license_object = {
        'name': 'my_license',
        'url': 'https://license-example.com',
    }

    assert swagger.validate_license_object(license_object) is None


def test_should_validate_license_object_unknown_field():
    license_object = {
        'name': 'my_license',
        'url': 'https://license-example.com',
        'author': 'john'
    }

    with pytest.raises(swagger.ValidationError):
        assert swagger.validate_license_object(license_object)


def test_should_validate_license_object_missing_field_name():
    license_object = {
        'url': 'https://license-example.com',
    }

    with pytest.raises(swagger.ValidationError):
        assert swagger.validate_license_object(license_object)


def test_should_validate_path_item_object():
    path_item_object = {
        "servers": {
            "url": "https://development.gigantic-server.com/v1",
        },
        "post": {
            "tags": [
                "users"
            ],
            "responses": {
                "201": {
                    "description": "Created user",
                    "headers": {
                        "description": "Location of the new item",
                        "schema": {
                            "type": "string"
                        }
                    },
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/UserModel"
                            },
                            "examples": {
                                "application/json": {
                                    "id": 1
                                }
                            }
                        }
                    }
                }
            }
        },
        '$ref': "",
        "parameters": [
            {
                "name": "body",
                "description": "Request body",
                "in": "query",
                "schema": {
                    "$ref": "#/components/schemas/UserModel"
                },
                "required": True
            }
        ],
        'summary': "Add a user",
        "description": "Adds a user",
    }

    assert swagger.validate_path_item_object(path_item_object) is None


def test_should_validate_path_item_object_invalid_field():
    with pytest.raises(swagger.ValidationError):
        assert swagger.validate_path_item_object({'some_invalid_field': 1})


def test_should_validate_operation_object():
    obj = {
        'tags': ['user'],
        'description': 'Returns a user',
        'deprecated': True,
        'responses': {
            '200': {
                'description': 'Get users',
                'content': {
                    'application/json': {
                        'schema': {
                            "$ref": "#/components/schemas/UserModel"
                        },
                        'examples': {
                            'application/json': {
                                'id': 1,
                                'name': 'somebody'
                            }
                        }
                    }
                }
            }
        },
        'requestBody': {
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/User"
                    },
                    "examples": {
                        "user": {
                            "summary": "User Example",
                            "externalValue": "http://foo.bar/examples/user-example.json"
                        }
                    }
                }
            }
        },
        'externalDocs': {
            "url": "https://example.com"
        },
        'security': {
            "api_key": []
        }
    }
    assert swagger.validate_operation_object(obj) is None


def test_should_validate_operation_object_invalid_field():
    with pytest.raises(swagger.ValidationError):
        assert swagger.validate_operation_object({'some_invalid_field': 1})


def test_should_validate_operation_object_no_responses():
    obj = {
        'tags': ['user'],
        'description': 'Returns a user',
        'deprecated': True,
        'requestBody': {
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/User"
                    },
                    "examples": {
                        "user": {
                            "summary": "User Example",
                            "externalValue": "http://foo.bar/examples/user-example.json"
                        }
                    }
                }
            }
        },
        'externalDocs': {
            "url": "https://example.com"
        },
        'security': {
            "api_key": []
        }
    }

    with pytest.raises(swagger.ValidationError):
        assert swagger.validate_operation_object(obj)


def test_should_validate_operation_object_tags_not_list():
    obj = {
        'tags': 'user',
        'description': 'Returns a user',
        'responses': {
            '200': {
                'description': 'Get users',
                'content': {
                    'application/json': {
                        'schema': {
                            "$ref": "#/components/schemas/UserModel"
                        },
                        'examples': {
                            'application/json': {
                                'id': 1,
                                'name': 'somebody'
                            }
                        }
                    }
                }
            }
        }
    }
    with pytest.raises(swagger.ValidationError):
        assert swagger.validate_operation_object(obj)


def test_should_validate_operation_object_summary_not_string():
    obj = {
        'tags': ['user'],
        'description': 'Returns a user',
        'summary': {},
        'responses': {
            '200': {
                'description': 'Get users',
                'content': {
                    'application/json': {
                        'schema': {
                            "$ref": "#/components/schemas/UserModel"
                        },
                        'examples': {
                            'application/json': {
                                'id': 1,
                                'name': 'somebody'
                            }
                        }
                    }
                }
            }
        }
    }
    with pytest.raises(swagger.ValidationError):
        assert swagger.validate_operation_object(obj)


def test_should_validate_operation_object_deprecated_not_bool():
    obj = {
        'tags': ['user'],
        'description': 'Returns a user',
        'deprecated': "deprecated",
        'responses': {
            '200': {
                'description': 'Get users',
                'content': {
                    'application/json': {
                        'schema': {
                            "$ref": "#/components/schemas/UserModel"
                        },
                        'examples': {
                            'application/json': {
                                'id': 1,
                                'name': 'somebody'
                            }
                        }
                    }
                }
            }
        }
    }
    with pytest.raises(swagger.ValidationError):
        assert swagger.validate_operation_object(obj)


def test_should_validate_parameter_object_parser():
    post_parser = RequestParser()
    post_parser.add_argument('id', type=int, help='id help')
    post_parser.add_argument('name', type=str)
    post_parser.add_argument('value', type=float, default=1.1)
    post_parser.add_argument('private', type=bool, required=True)
    post_parser.add_argument('type', type=str, choices=['common', 'major', 'minor'])

    parameter_object = {
        'reqparser': {'name': 'EntityAddParser',
                      'parser': post_parser},
    }
    assert swagger.validate_parameter_object(parameter_object) is None


def test_should_validate_parameter_object_name_not_in_reqparser():
    post_parser = RequestParser()
    post_parser.add_argument('id', type=int, help='id help')
    post_parser.add_argument('name', type=str)
    post_parser.add_argument('value', type=float, default=1.1)
    post_parser.add_argument('private', type=bool, required=True)
    post_parser.add_argument('type', type=str, choices=['common', 'major', 'minor'])

    parameter_object = {
        'reqparser': {
            'parser': post_parser
        }
    }

    with pytest.raises(swagger.ValidationError):
        assert swagger.validate_parameter_object(parameter_object)


def test_should_validate_parameter_object_parser_not_in_reqparser():
    post_parser = RequestParser()
    post_parser.add_argument('id', type=int, help='id help')
    post_parser.add_argument('name', type=str)
    post_parser.add_argument('value', type=float, default=1.1)
    post_parser.add_argument('private', type=bool, required=True)
    post_parser.add_argument('type', type=str, choices=['common', 'major', 'minor'])

    parameter_object = {
        'reqparser': {
            'name': 'my_parser'
        }
    }

    with pytest.raises(swagger.ValidationError):
        assert swagger.validate_parameter_object(parameter_object)


def test_should_validate_parameter_object_invalid_field():
    with pytest.raises(swagger.ValidationError):
        assert swagger.validate_parameter_object({'some_invalid_field': 1})


def test_should_validate_parameter_object_no_name_field():
    obj = {
        'description': 'Name to filter by',
        'schema': {
            'type': 'string',
        },
        'in': 'query'
    }

    with pytest.raises(swagger.ValidationError):
        swagger.validate_parameter_object(obj)


def test_should_validate_parameter_object_no_in_field():
    obj = {
        'name': 'name',
        'description': 'Name to filter by',
        'schema': {
            'type': 'string'
        }
    }

    with pytest.raises(swagger.ValidationError):
        swagger.validate_parameter_object(obj)


def test_should_validate_parameter_object_invalid_in_field():
    obj = {
        'name': 'name',
        'description': 'Name to filter by',
        'schema': {
            'type': 'string',
        },
        'in': 'some_invalid_field'
    }

    with pytest.raises(swagger.ValidationError):
        swagger.validate_parameter_object(obj)


def test_should_validate_parameter_object_body_no_schema():
    obj = {
        'name': 'name',
        'description': 'Name to filter by',
        'type': 'string',
        'in': 'body'
    }

    with pytest.raises(swagger.ValidationError):
        swagger.validate_parameter_object(obj)


def test_should_validate_parameter_object_no_type_field():
    obj = {
        'description': 'Name to filter by',
        'in': 'query'
    }

    with pytest.raises(swagger.ValidationError):
        swagger.validate_parameter_object(obj)


def test_should_validate_parameter_object_array_no_items_field():
    obj = {
        'name': 'name',
        'description': 'Name to filter by',
        'type': 'array',
        'in': 'query',
    }

    with pytest.raises(swagger.ValidationError):
        swagger.validate_parameter_object(obj)


def test_should_validate_reference_object_no_ref_field():
    with pytest.raises(swagger.ValidationError):
        swagger.validate_reference_object({})


def test_should_validate_reference_object_multiple_keys():
    with pytest.raises(swagger.ValidationError):
        swagger.validate_reference_object({'$ref': 1, 'other_field': 2})


def test_should_validate_responses_object():
    obj = {
        '2XX': {
            "description": "response"
        },
        '404': {
            "description": "Not found"
        }
    }
    assert swagger.validate_responses_object(obj) is None


def test_should_validate_response_object():
    obj = {
        "description": "A complex object array response",
        "content": {
            "application/json": {
                "schema": {
                    "type": "array",
                    "items": {
                        "$ref": "#/components/schemas/VeryComplexType"
                    }
                }
            }
        },
        "links": {
            "operationRef": "Get something"
        }
    }
    assert swagger.validate_response_object(obj) is None


def test_should_validate_response_object_invalid_field():
    with pytest.raises(swagger.ValidationError):
        swagger.validate_response_object({'some_invalid_field': 1})


def test_should_validate_response_object_no_description():
    obj = {
        "content": {
            "application/json": {
                "schema": {
                    "type": "array",
                    "items": {
                        "$ref": "#/components/schemas/VeryComplexType"
                    }
                }
            }
        }
    }

    with pytest.raises(swagger.ValidationError):
        swagger.validate_response_object(obj)


def test_should_validate_request_body_object():
    obj = {
        "description": "user to add to the system",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/User"
                },
                "examples": {
                    "user": {
                        "summary": "User Example",
                        "externalValue": "http://foo.bar/examples/user-example.json"
                    }
                }
            }
        },
        "required": True
    }

    assert swagger.validate_request_body_object(obj) is None


def test_should_validate_request_body_object_missing_content_field():
    obj = {
        "description": "user to add to the system",
        "required": True
    }

    with pytest.raises(swagger.ValidationError):
        swagger.validate_request_body_object(obj)


def test_should_validate_content_object_invalid_pattern():
    obj = {
        "app": {
            "schema": {
                "$ref": "#/components/schemas/User"
            }
        }
    }

    with pytest.raises(swagger.ValidationError):
        swagger.validate_content_object(obj)


def test_should_validate_schema_object_required_not_list():
    obj = {
        "properties": {
            "id": {
                "format": "int64",
                "type": "integer"
            },
            "keys": {
                "items": {
                    "$ref": "#/definitions/KeysModel"
                },
                "type": "array"
            },
            "mail": {
                "$ref": "#/definitions/EmailModel"
            },
            "name": {
                "type": "string"
            }
        },
        "required": "name",
        "type": "object"
    }

    with pytest.raises(swagger.ValidationError):
        swagger.validate_schema_object(obj)


def test_should_validate_server_object_not_dict_or_not_list():
    server = "https://example.com"

    with pytest.raises(swagger.ValidationError):
        swagger.validate_servers_object(server)


def test_should_validate_server_object_unknown_item():
    server = {"me": "http://localhost:5000"}

    with pytest.raises(swagger.ValidationError):
        swagger.validate_servers_object(server)


def test_should_validate_server_object_missing_field_url():
    sever = {"description": "test"}

    with pytest.raises(swagger.ValidationError):
        swagger.validate_servers_object(sever)


def test_should_validate_server_object_invalid_url():
    server = {
        "description": "my_sever",
        "url": "//localhost:5000",
        "variables": {
            "enum": ["var1", "var2"],
            "default": "var1"
        }
    }

    with pytest.raises(swagger.ValidationError):
        swagger.validate_servers_object(server)


def test_should_validate_server_object():
    server = {
        "description": "my_sever",
        "url": "http://localhost:5000",
        "variables": {
            "enum": ["var1", "var2"],
            "default": "var1"
        }
    }

    for k, v in server.items():
        if k == "variables":
            assert swagger.validate_server_variables_object(v) is None
        continue


def test_should_validate_invalid_email():
    email = "not_email"
    is_email = swagger.validate_email(email)
    assert not is_email


def test_should_validate_server_variables_object_unknown_item():
    server_variables = {"name": "test"}

    with pytest.raises(swagger.ValidationError):
        swagger.validate_server_variables_object(server_variables)


def test_should_validate_server_variables_object_enum_not_list():
    server_variables = {"enum": "test", "default": "test"}

    with pytest.raises(swagger.ValidationError):
        swagger.validate_server_variables_object(server_variables)


def test_should_validate_server_variables_object_enum_item_not_string():
    server_variables = {"enum": [{}, 1], "default": "test"}

    with pytest.raises(swagger.ValidationError):
        swagger.validate_server_variables_object(server_variables)


def test_should_validate_server_variables_object_missing_default():
    server_variables = {"enum": ["var1", "var2"], "description": "test"}

    with pytest.raises(swagger.ValidationError):
        swagger.validate_server_variables_object(server_variables)


def test_should_extract_swagger_path():
    assert swagger.extract_swagger_path('/path/<parameter>') == '/path/{parameter}'


def test_should_extract_swagger_path_extended():
    assert swagger.extract_swagger_path(
        '/<string(length=2):lang_code>/<string:id>/<float:probability>') == '/{lang_code}/{id}/{probability}'


def test_should_sanitize_doc():
    assert swagger.sanitize_doc('line1\nline2\nline3') == 'line1<br/>line2<br/>line3'


def test_should_sanitize_doc_multi_line():
    assert swagger.sanitize_doc(['line1\nline2', None, 'line3\nline4']) == 'line1<br/>line2<br/>line3<br/>line4'


def test_should_parse_method_doc():
    def test_func(a):
        """
        Test function
        :param a: argument
        :return: Nothing
        """

    assert swagger.parse_method_doc(test_func, {}) == 'Test function'


def test_should_parse_method_doc_append_summary():
    def test_func(a):
        """
        Test function
        :param a: argument
        :return: Nothing
        """

    assert swagger.parse_method_doc(test_func, {'summary': 'Summary'}) == 'Summary<br/>Test function'


def test_should_parse_schema_doc():
    test_model = SwaggerTestModel()
    assert swagger.parse_schema_doc(test_model, {}) == 'Test schema model.'


def test_should_parse_schema_doc_existing_description():
    test_model = SwaggerTestModel()
    assert swagger.parse_schema_doc(test_model, {'description': 'Test description'}) is None
