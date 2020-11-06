from flask import request
from flask_restful.reqparse import RequestParser
from flask_restful_swagger_3 import Resource, swagger
from tests.fixtures.fixture_models import user_model, p_model, model_to_parse


def parse_resource():
    parse_resource_params = [
                {
                    'name': 'str',
                    'description': 'String value',
                    'in': 'query',
                    'schema': {
                        'type': 'string'
                    }
                },
                {
                    'name': 'date',
                    'description': 'Date value',
                    'in': 'query',
                    'schema': {
                        'type': 'string',
                        'format': 'date'
                    }
                },
                {
                    'name': 'datetime',
                    'description': 'Date-time value',
                    'in': 'query',
                    'schema': {
                        'type': 'string',
                        'format': 'date-time'
                    }
                },
                {
                    'name': 'bool',
                    'description': 'Boolean value',
                    'in': 'query',
                    'schema': {
                        'type': 'boolean'
                    }
                },
                {
                    'name': 'int',
                    'description': 'Integer value',
                    'in': 'query',
                    'schema': {
                        'type': 'integer'
                    }
                },
                {
                    'name': 'float',
                    'description': 'Float value',
                    'in': 'query',
                    'schema': {
                        'type': 'number',
                        'format': 'float'
                    }
                },
                {
                    'name': 'parsing',
                    'description': 'Parsing model',
                    'in': 'query',
                    'schema': model_to_parse()
                }
            ]

    class ParseResource(Resource):
        @swagger.response(200, description="Queries values")
        @swagger.parameters(parse_resource_params)
        def get(self, _parser):
            """
            Returns query parameters.
            :param _parser: parser containing data of query in url
            """
            args = _parser.parse_args()

            return {
                       'str': args.str,
                       'date': args.date.isoformat(),
                       'datetime': args.datetime.isoformat(),
                       'bool': args.bool,
                       'int': args.int,
                       'float': args.float,
                       'parsing': args.parsing
                   }, 200

    return ParseResource


def user_resource():
    class UserResource(Resource):
        @swagger.reorder_with(user_model(), response_code=200, description="Get users")
        @swagger.response(400, description="bad request")
        @swagger.parameter({
                    'name': 'name',
                    'description': 'User name',
                    'in': 'query',
                    'schema': {
                        'type': 'string'
                    }
                })
        def get(self, user_id, _parser):
            """
            Returns a specific user.
            :param user_id: The user identifier
            :param _parser: parser containing data of query in url
            """
            args = _parser.parse_args()

            name = args.get('name', 'somebody')
            return user_model()(**{'id': user_id, 'name': name, 'password': 'test'}), 200

        @swagger.response(204, description="No content", no_content=True)
        def delete(self, user_id):
            return f"User {user_id} deleted", 204

        @swagger.response(201, description="post")
        @swagger.expected(user_model())
        def post(self):
            return swagger.payload(), 201

    return UserResource


def no_converter_resource():
    class NoConverterResource(Resource):
        @swagger.response(200, description="Get users")
        def get(self, user_id):
            """
            Returns a specific user.
            :param user_id: The user identifier
            """
            return user_model()(**{'id': user_id}), 200

    return NoConverterResource


def bad_schema_resource_in_parameters():
    class BadSchemaResourceInParameters(Resource):
        @swagger.reorder_with(user_model(), response_code=200, description="Get users")
        @swagger.parameters([
            {
                'name': 'name',
                'description': 'User name',
                'in': 'query',
                'schema': 'string'
            }
        ])
        @swagger.parameter(
                    name='name',
                    description='User name',
                    _in='query',
                    schema='string'
                )
        def get(self, user_id, _parser):
            pass

    return BadSchemaResourceInParameters


def bad_resource_parameter_type():
    class BadResourceParameterType(Resource):
        @swagger.reorder_with(user_model(), response_code=200, description="Get users")
        @swagger.parameter(param="test")
        def get(self, user_id, _parser):
            pass

    return BadResourceParameterType


def bad_resource_parameters_type():
    class BadResourceParametersType(Resource):
        @swagger.reorder_with(user_model(), response_code=200, description="Get users")
        @swagger.parameters({
                'name': 'name',
                'description': 'User name',
                'in': 'query',
                'schema': 'string'
            })
        def get(self, user_id, _parser):
            pass

    return BadResourceParametersType


def bad_resource_parameters_in_is_path():
    class BadResourceParametersIn(Resource):
        @swagger.reorder_with(user_model(), response_code=200, description="Get users")
        @swagger.parameter({
                'name': 'name',
                'description': 'User name',
                'in': 'path',
                'schema': 'string'
            })
        def get(self, user_id, _parser):
            pass

    return BadResourceParametersIn


def entity_add_resource():
    class EntityAddResource(Resource):
        post_parser = RequestParser()
        post_parser.add_argument('id', type=int, help='id help')
        post_parser.add_argument('name', type=str)
        post_parser.add_argument('value', type=float, default=1.1)
        post_parser.add_argument('private', type=bool, required=True)
        post_parser.add_argument('type', type=str, choices=['common', 'major', 'minor'])

        class PasswordType(str):
            swagger_type = 'password'
        post_parser.add_argument('password_arg', type=PasswordType, required=False)

        @swagger.response(response_code=200, description='User')
        @swagger.reqparser(name='EntityAddParser', parser=post_parser)
        def post(self):
            """
            Returns a specific user.
            """
            args = self.post_parser.parse_args()

            name = args.get('name', 'somebody')
            return user_model()(**{'id': args.get('id', 2), 'name': name}), 200

    return EntityAddResource


def bad_format_resource():
    class BadFormatResourceReqbodyReqparser(Resource):
        post_parser = RequestParser()
        post_parser.add_argument('id', type=int, help='id help')
        post_parser.add_argument('name', type=str)
        post_parser.add_argument('value', type=float, default=1.1)
        post_parser.add_argument('private', type=bool, required=True)
        post_parser.add_argument('type', type=str, choices=['common', 'major', 'minor'])

        @swagger.expected(user_model(), True)
        @swagger.reqparser(name='parser', parser=post_parser)
        def post(self):
            pass

    return BadFormatResourceReqbodyReqparser


def bad_format_url():
    class BadFormatUrl(Resource):

        @swagger.response(200)
        def get(self):
            pass

    return BadFormatUrl


def p_resource():
    class PResource(Resource):
        @swagger.tags('User')
        @swagger.reorder_with(p_model(), response_code=201)
        @swagger.response(400, description="bad request")
        @swagger.response(500, description="internal server error")
        @swagger.parameters([
            {'in': 'query',
             'name': 'body',
             'description': 'Request body',
             'schema': p_model(),
             'required': 'true'}
        ])
        def post(self, _parser):
            """Adds a user."""
            # Validate request body with schema model
            args = _parser.parse_args()
            try:
                data = p_model()(**args)
            except ValueError as e:
                return {'message': e.args[0]}, 400

            return data, 201, {'Location': request.path + '/' + str(data['id'])}

        @swagger.tags('User')
        @swagger.reorder_list_with(p_model(), response_code=200)
        def get(self):
            """Get something"""
            pass

    return PResource


def one_resource():
    @swagger.tags('Some data')
    class OneResource(Resource):
        @swagger.response(200, description="Some data")
        def get(self):
            return {'data': 'some data'}, 200

    return OneResource

