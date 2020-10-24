import pytest
from flask_restful import inputs

import flask_restful_swagger_3.swagger as swagger


class TestSwagger:

    def test_should_set_nested(self):
        d = {'openapi': '3.0.0'}
        swagger.set_nested(d, 'info.title', 'API')
        assert d == {'openapi': '3.0.0', 'info': {'title': 'API'}}

    def test_should_get_data_type_str(self):
        assert swagger.get_data_type({'type': 'string'}) == str

    def test_should_get_data_type_str_date(self):
        assert swagger.get_data_type({'type': 'string', 'format': 'date'}) == inputs.date

    def test_should_get_data_type_str_date_time(self):
        assert swagger.get_data_type(
            {'type': 'string', 'format': 'date-time'}) == inputs.datetime_from_iso8601

    def test_should_get_data_type_int(self):
        assert swagger.get_data_type({'type': 'integer'}) == int

    def test_should_get_data_type_bool(self):
        assert swagger.get_data_type({'type': 'boolean'}) == inputs.boolean

    def test_should_get_data_type_float(self):
        assert swagger.get_data_type({'type': 'number', 'format': 'float'}) == float

    def test_should_get_data_type_double(self):
        assert swagger.get_data_type({'type': 'number', 'format': 'double'}) == float

    def test_should_get_data_type_invalid(self):
        assert swagger.get_data_type({}) is None

    def test_should_get_data_type_without_type(self):
        assert swagger.get_data_type({'schema': {}}) is None

    def test_should_get_parser_arg(self):
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
            'choices': (),
            'action': 'store'
        })

        assert swagger.get_parser_arg(param) == expected

    def test_should_get_parser_arg_with_default(self):
        param = {
            'name': 'name',
            'description': 'Name to filter by',
            'schema': {
                'type': 'string',
                'default': 'something'
            },
            'in': 'query'
        }

        expected = ('name', {
            'dest': 'name',
            'type': str,
            'location': 'args',
            'help': 'Name to filter by',
            'required': False,
            'default': 'something',
            'choices': (),
            'action': 'store'
        })

        assert swagger.get_parser_arg(param) == expected

    def test_should_get_parser_arg_with_choices(self):
        param = {
            'name': 'name',
            'description': 'Name to filter by',
            'schema': {
                'type': 'string',
                'default': 'something',
                'enum': ['first', 'second']
            },
            'in': 'query'
        }

        expected = ('name', {
            'dest': 'name',
            'type': str,
            'location': 'args',
            'help': 'Name to filter by',
            'required': False,
            'default': 'something',
            'choices': ('first', 'second'),
            'action': 'store'
        })

        assert swagger.get_parser_arg(param) == expected

    def test_get_parser_arg_should_raises_error_when_enum_not_list_set_or_tuple(self):
        param = {
            'name': 'name',
            'description': 'Name to filter by',
            'schema': {
                'type': 'string',
                'default': 'something',
                'enum': "first, second"
            },
            'in': 'query'
        }

        with pytest.raises(TypeError):
            swagger.get_parser_arg(param)

    def test_should_get_parser_args(self):
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
            'choices': (),
            'action': 'store'
        })]

        assert swagger.get_parser_args(params) == expected

    def test_array_get_parser_args(self):
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
            'choices': (),
            'action': 'append'
        })]

        assert swagger.get_parser_args(params) == expected

    def test_should_get_parser(self):
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

    def test_should_get_data_action_is_none(self):
        assert swagger.get_data_action({}) is None

    def test_should_validate_info_object_unknown_field(self):
        info_object = {
            'title': 'test',
            'description': 'my description',
            'version': '0.1',
            'artist': 'Picasso'
        }

        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_info_object(info_object)

    def test_should_validate_info_object_missing_title(self):
        info_object = {
            'description': 'my description',
            'version': '0.1',
        }

        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_info_object(info_object)

    def test_should_validate_info_object_missing_version(self):
        info_object = {
            'title': 'test',
            'description': 'my description',
        }

        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_info_object(info_object)

    def test_should_validate_contact_object(self):
        contact_object = {
            'name': 'John',
            'url': 'test@example.com',
            'email': 'john.doe@example.com'
        }

        assert swagger.validate_contact_object(contact_object) is None

    def test_should_validate_contact_object_unknown_field(self):
        contact_object = {
            'author': 'John'
        }

        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_contact_object(contact_object)

    def test_should_validate_license_object(self):
        license_object = {
            'name': 'my_license',
            'url': 'https://license-example.com',
        }

        assert swagger.validate_license_object(license_object) is None

    def test_should_validate_license_object_unknown_field(self):
        license_object = {
            'name': 'my_license',
            'url': 'https://license-example.com',
            'author': 'john'
        }

        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_license_object(license_object)

    def test_should_validate_license_object_missing_field_name(self):
        license_object = {
            'url': 'https://license-example.com',
        }

        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_license_object(license_object)

    def test_should_validate_path_item_object(self):
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

    def test_should_validate_path_item_object_invalid_field(self):
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_path_item_object({'some_invalid_field': 1})

    def test_should_validate_operation_object(self):
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

    def test_should_validate_operation_object_invalid_field(self):
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_operation_object({'some_invalid_field': 1})

    def test_should_validate_operation_object_no_responses(self):
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

    def test_should_validate_operation_object_tags_not_list(self):
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
                            }
                        }
                    }
                }
            }
        }
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_operation_object(obj)

    def test_should_concatenate_multiple_urls(self):
        urls = ['/api/', '/doc', 'sub_doc/', 'file']
        assert swagger.slash_join(*urls) == '/api/doc/sub_doc/file'
