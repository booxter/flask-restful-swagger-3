from flask import request, Blueprint
from flask_restful.reqparse import RequestParser

from flask_restful_swagger_3 import Api, swagger, Resource

from models import UserModel, ErrorModel


known_users = []


class UserResource(Resource):
    @swagger.tags('users')
    @swagger.reorder_with(UserModel, response_code=200)
    @swagger.parameter(_in='query', name='query', schema=UserModel, required=True, description='query')
    def post(self, _parser):
        """
        Adds a user
        """
        # Validate request body with schema model
        try:
            data = UserModel(**_parser.parse_args())

        except ValueError as e:
            return ErrorModel(**{'message': e.args[0]}), 400

        data['id'] = len(known_users) + 1
        known_users.append(data)

        return data, 201, {'Location': request.path + '/' + str(data['id'])}

    @swagger.tags('users')
    @swagger.response(response_code=200)
    def get(self):
        """
        Returns all users.
        """
        users = ([u for u in known_users if u['name']])

        # Return data through schema model
        return list(map(lambda user: UserModel(**user), users)), 200
        # return "success"


class UserItemResource(Resource):
    @swagger.tags('user')
    @swagger.response(response_code=200)
    def get(self, user_id):
        """
        Returns a specific user.
        :param user_id: The user identifier
        """
        user = next((u for u in known_users if u['id'] == user_id), None)

        if user is None:
            return ErrorModel(**{'message': "User id {} not found".format(user_id)}), 404

        # Return data through schema model
        return UserModel(**user), 200


def get_user_resources():
    """
    Returns user resources.
    :param app: The Flask instance
    :return: User resources
    """
    blueprint = Blueprint('user', __name__)

    api = Api(blueprint)

    api.add_resource(UserResource, '/api/users')
    api.add_resource(UserItemResource, '/api/users/<int:user_id>')

    return api
