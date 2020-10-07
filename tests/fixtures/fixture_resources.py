import sys
from flask import request
from flask_restful.reqparse import RequestParser
from flask_restful_swagger_3 import Resource, swagger
from tests.fixtures.fixture_models import UserModel, PModel


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
            }
        ]


class ParseResource(Resource):
    @swagger.response(200, description="Quries values")
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
                   'float': args.float
               }, 200


class UserResource(Resource):
    @swagger.reorder_with(UserModel, response_code=200, description="Get users")
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
        return UserModel(**{'id': user_id, 'name': name}), 200

    @swagger.response(204, description="No content", no_content=True)
    def delete(self, user_id):
        return f"User {user_id} deleted", 204


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
        return UserModel(**{'id': id, 'name': name}), 200


class BadFormatResourceReqbodyReqparser(Resource):
    post_parser = RequestParser()
    post_parser.add_argument('id', type=int, help='id help')
    post_parser.add_argument('name', type=str)
    post_parser.add_argument('value', type=float, default=1.1)
    post_parser.add_argument('private', type=bool, required=True)
    post_parser.add_argument('type', type=str, choices=['common', 'major', 'minor'])

    @swagger.expected(UserModel, True)
    @swagger.reqparser(name='parser', parser=post_parser)
    def post(self):
        pass


class BadFormatUrl(Resource):

    def get(self):
        pass


class PResource(Resource):
    @swagger.tags('User')
    @swagger.reorder_with(PModel, response_code=201)
    @swagger.parameters([
        {'in': 'query',
         'name': 'body',
         'description': 'Request body',
         'schema': PModel,
         'required': 'true'}
    ])
    def post(self, _parser):
        """Adds a user."""
        # Validate request body with schema model
        args = _parser.parse_args()
        try:
            data = PModel(**args)
            print(data)
        except ValueError as e:
            return {'message': e.args[0]}, 400

        return data, 201, {'Location': request.path + '/' + str(data['id'])}

