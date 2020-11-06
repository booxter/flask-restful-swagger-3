import pytest
from flask_restful import inputs

import flask_restful_swagger_3.swagger as swagger
from flask_restful_swagger_3 import Schema


class TestSwagger:

    def test_should_set_nested(self):
        d = {'openapi': '3.0.0'}
        swagger.set_nested(d, 'info.title', 'API')
        assert d == {'openapi': '3.0.0', 'info': {'title': 'API'}}

    def test_should_add_parameters(self):
        d = {'openapi': '3.0.0'}
        swagger.add_parameters(d, {'title': 'title', 'description': 'description'})
        assert d == {'openapi': '3.0.0', 'info': {'title': 'title', 'description': 'description'}}

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

    def test_should_get_data_type_of_obj(self):
        class String(Schema):
            type = 'string'

        class Scheme1(Schema):
            type = 'object'
            properties = {
                'fake': {
                    'type': 'string'
                },
                'fake2': String
            }
        assert swagger.get_data_type(Scheme1.array()) == str

    def test_get_parser_from_schema(self):
        class Scheme2(Schema):
            type = 'object'
            properties = {
                'fake': {
                    'type': 'string'
                },
                'fake2': {
                    'type': 'integer'
                }
            }

        parser_result = list(swagger.get_parser_from_schema({'schema': {'$ref': Scheme2}}))

        assert parser_result[0][0] == 'fake'
        assert parser_result[0][1] == {
            'dest': 'fake', 'type': str, 'location': 'args', 'help': None,
            'required': False, 'default': None, 'choices': (), 'action': 'store'
        }

        assert parser_result[1][0] == 'fake2'
        assert parser_result[1][1] == {
            'dest': 'fake2', 'type': int, 'location': 'args', 'help': None,
            'required': False, 'default': None, 'choices': (), 'action': 'store'
        }

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

    def test_should_validate_contact_object_bad_email(self):
        contact_object = {
            'email': 'John'
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

    def test_should_validate_license_object_bad_url(self):
        license_object = {
            'name': 'my_license',
            'url': 'url',
        }

        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_license_object(license_object)

    def test_should_validate_path_item_object(self, path_item_object):
        assert swagger.validate_path_item_object(path_item_object) is None

    def test_should_validate_path_item_object_invalid_field(self):
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_path_item_object({'some_invalid_field': 1})

    def test_should_validate_operation_object(self, components_security_schemes_object, operation_object):
        """We must validate the security schemes object before validate the operation object to check the security
        """
        assert swagger.validate_map_security_scheme_object(components_security_schemes_object['securitySchemes']) is None
        assert swagger.validate_operation_object(operation_object) is None

    def test_should_validate_operation_object_invalid_description(self, operation_object):
        operation_object['description'] = 3
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_operation_object(operation_object)

    def test_should_validate_operation_object_invalid_deprecated(self, operation_object):
        operation_object['deprecated'] = 'deprecated'
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_operation_object(operation_object)

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

    def test_validate_parameter_object(self, parameter_object):
        assert swagger.validate_parameter_object(parameter_object) is None

    def test_validate_parameter_object_unknown_field(self, parameter_object):
        parameter_object['unknown'] = 'no'
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_parameter_object(parameter_object)

    def test_validate_parameter_object_missing_name(self, parameter_object):
        del parameter_object['name']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_parameter_object(parameter_object)

    def test_validate_parameter_object_missing_in(self, parameter_object):
        del parameter_object['in']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_parameter_object(parameter_object)

    def test_validate_parameter_object_invalid_in(self, parameter_object):
        parameter_object['in'] = "something else"
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_parameter_object(parameter_object)

    def test_validate_responses_object(self, responses_object):
        assert swagger.validate_responses_object(responses_object) is None

    def test_validate_responses_object_not_int_or_str(self, responses_object):
        responses_object[(2, 3)] = {}
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_responses_object(responses_object) is None

    def test_validate_responses_object_not_http_status_code_or_default(self, responses_object):
        responses_object[98] = {}
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_responses_object(responses_object) is None

        responses_object['other'] = {}
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_responses_object(responses_object) is None

    def test_validate_responses_object_is_reference(self, responses_object):
        responses_object['200'] = {"$ref": "#/components/responses/200OK"}
        assert swagger.validate_responses_object(responses_object) is None

    def test_validate_response_object(self, responses_object):
        response_object = responses_object["default"]
        response_object['headers'] = {"$ref": "#/components/schemas/CategoryDumpSchema"}
        response_object['links'] = {"operationRef": 'my_ref'}
        assert swagger.validate_response_object(response_object) is None

    def test_validate_response_object_with_headers(self, responses_object):
        response_object = responses_object["default"]
        response_object['headers'] = {
            'X-Something-Bidule': {
                "description": "Location of the new item",
                "schema": {
                    "type": "string"
                }
            },
        }
        response_object['links'] = {"operationRef": 'my_ref'}
        assert swagger.validate_response_object(response_object) is None

    def test_validate_response_object_unknown_field(self, responses_object):
        response_object = responses_object["default"]
        response_object['unknown'] = 'unknown'
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_response_object(response_object)

    def test_validate_response_object_missing_description(self, responses_object):
        response_object = responses_object["default"]
        del response_object['description']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_response_object(response_object)

    def test_validate_request_body_object_missing_content(self, request_body):
        del request_body['content']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_request_body_object(request_body)

    def test_validate_content_object_bad_pattern(self, request_body):
        content = request_body['content']
        content['test'] = 'other'
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_map_media_type_object(content)

    def test_validate_components_schemas_object(self, components_schemas_object):
        assert swagger.validate_components_object(components_schemas_object) is None

    def test_validate_components_schemas_object_unknown_field(self, components_schemas_object):
        components_schemas_object['unknown'] = {}
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_schemas_object) is None

    def test_validate_components_schemas_object_required_not_list(self, components_schemas_object):
        components_schemas_object['schemas']['RequiredSchema']['required'] = 'not list'
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_schemas_object)

    def test_validate_components_responses_object(self, components_responses_object):
        assert swagger.validate_components_object(components_responses_object) is None

    def test_validate_components_parameters_object(self, components_parameters_object):
        assert swagger.validate_components_object(components_parameters_object) is None

    def test_validate_components_examples_object(self, components_examples_object):
        assert swagger.validate_components_object(components_examples_object) is None

    def test_validate_components_examples_object_summary_not_str(self, components_examples_object):
        components_examples_object['examples']['CategoryExample']['summary'] = True
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_examples_object)

    def test_validate_components_request_bodies_object(self, components_request_bodies_object):
        assert swagger.validate_components_object(components_request_bodies_object) is None

    def test_validate_components_headers_object(self, components_headers_object):
        assert swagger.validate_components_object(components_headers_object) is None

    def test_validate_components_headers_object_raise_error_when_name_is_specified(self, components_headers_object):
        components_headers_object['headers']['X-Something-Bidule']['name'] = "name"
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_headers_object)

    def test_validate_components_headers_object_raise_error_when_in_is_specified(self, components_headers_object):
        components_headers_object['headers']['X-Something-Bidule']['in'] = "in"
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_headers_object)

    def test_validate_components_security_schemes_object(self, components_security_schemes_object):
        assert swagger.validate_components_object(components_security_schemes_object) is None

    def test_validate_components_security_schemes_object_type_not_specified(self, components_security_schemes_object):
        del components_security_schemes_object['securitySchemes']['auth']['type']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_type_not_in_choices(self, components_security_schemes_object):
        components_security_schemes_object['securitySchemes']['auth']['type'] = "other"
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_name_missing_when_type_is_api_key(
            self, components_security_schemes_object):
        del components_security_schemes_object['securitySchemes']['api-key']['name']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_in_missing_when_type_is_api_key(
            self, components_security_schemes_object):
        del components_security_schemes_object['securitySchemes']['api-key']['in']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_scheme_missing_when_type_is_http(
            self, components_security_schemes_object):
        del components_security_schemes_object['securitySchemes']['http']['scheme']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_scheme_bad_choice(
            self, components_security_schemes_object):
        components_security_schemes_object['securitySchemes']['http']['scheme'] = 'bad_choice'
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_open_id_connect_url_missing_when_type_is_open_id_connect(
            self, components_security_schemes_object):
        del components_security_schemes_object['securitySchemes']['openId']['openIdConnectUrl']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_open_id_connect_url_bad_url_format(
            self, components_security_schemes_object):
        components_security_schemes_object['securitySchemes']['openId']['openIdConnectUrl'] = 'url'
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_flows_missing_when_type_is_oauth2(
            self, components_security_schemes_object):
        del components_security_schemes_object['securitySchemes']['auth']['flows']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_flows_bad_choice(
            self, components_security_schemes_object):
        del components_security_schemes_object['securitySchemes']['auth']['flows']['implicit']
        components_security_schemes_object['securitySchemes']['auth']['flows']['bad_choice'] = {}
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_flows_unknown_fields(
            self, components_security_schemes_object):
        components_security_schemes_object['securitySchemes']['auth']['flows']['implicit']['unknown'] = 'unknown'
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_flows_missing_scopes(
            self, components_security_schemes_object):
        del components_security_schemes_object['securitySchemes']['auth']['flows']['implicit']['scopes']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_flows_scopes_bad_items_type(
            self, components_security_schemes_object):
        components_security_schemes_object['securitySchemes']['auth']['flows']['implicit']['scopes']['write:pets'] = True
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_flows_scopes_bad_type(
            self, components_security_schemes_object):
        components_security_schemes_object['securitySchemes']['auth']['flows']['implicit']['scopes'] = 'write:pets'
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_flows_missing_authorization_url(
            self, components_security_schemes_object):
        del components_security_schemes_object['securitySchemes']['auth']['flows']['implicit']['authorizationUrl']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_flows_authorization_url_bad_url_format(
            self, components_security_schemes_object):
        components_security_schemes_object['securitySchemes']['auth']['flows']['implicit']['authorizationUrl'] = 'url'
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_flows_missing_token_url(
            self, components_security_schemes_object):
        del components_security_schemes_object['securitySchemes']['auth-password']['flows']['password']['tokenUrl']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_flows_token_url_bad_url_format(
            self, components_security_schemes_object):
        components_security_schemes_object['securitySchemes']['auth-password']['flows']['password']['tokenUrl'] = 'url'
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_security_schemes_object_flows_refresh_url_bad_url_format(
            self, components_security_schemes_object):
        components_security_schemes_object['securitySchemes']['auth-authorizationCode']['flows']['authorizationCode']['refreshUrl'] = 'url'
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_security_schemes_object)

    def test_validate_components_link_object(self, components_link_object):
        assert swagger.validate_components_object(components_link_object) is None

    def test_validate_components_link_object_operation_ref_is_not_str(self, components_link_object):
        components_link_object['links']['UserRepositories']['operationRef'] = 1
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_link_object) is None

    def test_validate_components_link_object_operation_id_is_not_str(self, components_link_object):
        components_link_object['links']['UserRepositories']['operationId'] = 2
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_link_object) is None

    def test_validate_components_link_object_description_is_not_str(self, components_link_object):
        components_link_object['links']['UserRepositories']['description'] = 3
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_components_object(components_link_object) is None

    def test_validate_components_callback_object(self, components_callback_object):
        assert swagger.validate_components_object(components_callback_object) is None

    def test_validate_server_object(self, server_object):
        assert swagger.validate_server_object(server_object) is None

    def test_validate_server_object_unknown_field(self, server_object):
        server_object['unknown'] = "unknown"
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_server_object(server_object)

    def test_validate_server_object_url_bad_format(self, server_object):
        server_object['url'] = "url"
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_server_object(server_object)

    def test_validate_server_object_missing_url(self, server_object):
        del server_object['url']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_server_object(server_object)

    def test_validate_server_object_not_dict(self):
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_server_object("server")

    def test_validate_servers_object_list_ok(self, server_object):
        servers = [server_object]
        assert swagger.validate_servers_object(servers) is None

    def test_validate_servers_object_not_list(self, server_object):
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_servers_object(server_object) is None

    def test_validate_server_variables_object_unknown_fields(self, server_object):
        variables = server_object['variables']
        variables['unknown'] = "unknown"
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_server_variables_object(variables)

    def test_validate_server_variables_object_enum_no_list(self, server_object):
        variables = server_object['variables']
        variables['enum'] = "enum"
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_server_variables_object(variables)

    def test_validate_server_variables_object_some_enum__items_not_str(self, server_object):
        variables = server_object['variables']
        variables['enum'].append(2)
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_server_variables_object(variables)

    def test_validate_server_variables_object_missing_default(self, server_object):
        variables = server_object['variables']
        del variables['default']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_server_variables_object(variables)

    def test_sanitize_doc(self):
        assert swagger.sanitize_doc(["desciption1", "description2"]) == "desciption1<br/>description2"

    def test_validate_open_api_object(self, open_api_object):
        assert swagger.validate_open_api_object(open_api_object) is None

    def test_validate_open_api_object_unknown_field(self, open_api_object):
        open_api_object['unknown'] = ""
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_open_api_object(open_api_object)

    def test_validate_open_api_object_bad_openapi_field_type(self, open_api_object):
        open_api_object['openapi'] = 2.0
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_open_api_object(open_api_object)

    def test_validate_open_api_object_missing_openapi_field(self, open_api_object):
        del open_api_object['openapi']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_open_api_object(open_api_object)

    def test_validate_open_api_object_missing_info_field(self, open_api_object):
        del open_api_object['info']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_open_api_object(open_api_object)

    def test_validate_open_api_object_missing_paths_field(self, open_api_object):
        del open_api_object['paths']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_open_api_object(open_api_object)

    def test_validate_paths_object(self, paths_object):
        assert swagger.validate_paths_object(paths_object) is None

    def test_validate_paths_object_bad_type(self, paths_object):
        paths_object[2] = {}
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_paths_object(paths_object) is None

    def test_validate_paths_object_not_start_with_leading_slash(self, paths_object):
        paths_object['some_path'] = {}
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_paths_object(paths_object) is None

    def test_validate_paths_object_end_with_slash(self, paths_object):
        paths_object['/some_path/'] = {}
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_paths_object(paths_object) is None

    def test_validate_external_documentation_object(self, external_documentation_object):
        assert swagger.validate_external_documentation_object(external_documentation_object) is None

    def test_validate_external_documentation_object_unknown_fields(self, external_documentation_object):
        external_documentation_object['unknown'] = 'unknown'
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_external_documentation_object(external_documentation_object) is None

    def test_validate_external_documentation_object_description_bad_type(self, external_documentation_object):
        external_documentation_object['description'] = 2
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_external_documentation_object(external_documentation_object) is None

    def test_validate_external_documentation_object_missing_url(self, external_documentation_object):
        del external_documentation_object['url']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_external_documentation_object(external_documentation_object) is None

    def test_validate_security(self, components_security_schemes_object, security):
        """We must validate the security schemes object before validate the security"""
        assert swagger.validate_map_security_scheme_object(components_security_schemes_object['securitySchemes']) is None
        assert swagger.validate_security(security) is None

    def test_validate_security_not_list(self, components_security_schemes_object, security):
        """We must validate the security schemes object before validate the security"""
        assert swagger.validate_map_security_scheme_object(components_security_schemes_object['securitySchemes']) is None
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_security({
                "api-key": ''
            }) is None

    def test_validate_security_item_not_list(self, components_security_schemes_object, security):
        """We must validate the security schemes object before validate the security"""
        assert swagger.validate_map_security_scheme_object(components_security_schemes_object['securitySchemes']) is None
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_security([{
                "api-key": ''
            }]) is None

    def test_validate_security_not_in_security_schemes(self, components_security_schemes_object, security):
        """We must validate the security schemes object before validate the security"""
        assert swagger.validate_map_security_scheme_object(components_security_schemes_object['securitySchemes']) is None
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_security([
                {
                    "api_key": []
                }
            ]) is None

    def test_validate_security_schemes_object_not_exist(self, components_security_schemes_object, security):
        """We must validate the security schemes object before validate the security"""
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_security([
                {
                    "api_key": []
                }
            ]) is None

    def test_validate_security_schemes_object_must_be_empty(self, components_security_schemes_object, security):
        """We must validate the security schemes object before validate the security"""
        assert swagger.validate_map_security_scheme_object(components_security_schemes_object['securitySchemes']) is None
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_security([
                {
                    "api-key": [{
                        'scopes': ''
                    }]
                }
            ]) is None

    def test_validate_example_object(self, example_object):
        assert swagger.validate_example_object(example_object) is None

    def test_validate_example_object_unknown_field(self, example_object):
        example_object['unknown'] = ''
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_example_object(example_object) is None

    def test_validate_tags_object(self, tags_object):
        assert swagger.validate_tags(tags_object) is None

    def test_validate_tags_object_not_list(self):
        tags_object = {}
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_tags(tags_object) is None

    def test_validate_tag_object_unknown_field(self, tags_object):
        tags_object[0]['unknown'] = ''
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_tags(tags_object) is None

    def test_validate_tag_object_description_bad_type(self, tags_object):
        tags_object[0]['description'] = 1
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_tags(tags_object) is None

    def test_validate_tag_object_missing_name_field(self, tags_object):
        del tags_object[0]['name']
        with pytest.raises(swagger.ValidationError):
            assert swagger.validate_tags(tags_object) is None

    def test_validate_media_type(self, media_types):

        for test in media_types[:-1]:
            assert swagger.validate_media_type(test)

    def test_not_validate_media_type_bad_format(self, media_types):

        assert not swagger.validate_media_type(media_types[-1])
