from flask import request
from flask_restful.reqparse import RequestParser

from flask_restful_swagger_3 import swagger, Resource

from models import UserModel, ErrorModel


known_users = []


class UserResource(Resource):
    @swagger.tags('User')
    @swagger.reorder_with(UserModel, response_code=200)
    @swagger.parameters([{'in':'query', 'name':'body', 'description':'Request body', 'schema':UserModel, 'required': 'true'}])
    def post(self, _parser):
        """Adds a user."""
        # Validate request body with schema model
        print("Ma valeur retournée", _parser.parse_args()['name'])
        try:
            data = UserModel(**_parser.parse_args())

        except ValueError as e:
            return ErrorModel(**{'message': e.args[0]}), 400

        data['id'] = len(known_users) + 1
        known_users.append(data)

        return data, 201, {'Location': request.path + '/' + str(data['id'])}

    @swagger.tags('User')
    @swagger.reorder_with(UserModel, response_code=200)
    @swagger.parameters(
        [{'in': 'query', 'name': 'body', 'description': 'Request body', 'schema': {'type': 'string'}, 'required': 'true'}])
    def get(self, _parser):
        """Returns all users."""
        # swagger.doc decorator returns a query parameter parser in the special
        # '_parser' function argument if it is present
        args = _parser.parse_args()

        users = ([u for u in known_users if u['name'] == args['name']]
                 if 'name' in args else known_users)

        # Return data through schema model
        return list(map(lambda user: UserModel(**user), users)), 200


class UserItemResource(Resource):
    @swagger.tags('usersItem')
    @swagger.reorder_with(UserModel, response_code=200)
    @swagger.response(response_code=404)
    def get(self, user_id):
        """Returns a specific user."""
        user = next((u for u in known_users if u['id'] == user_id), None)

        if user is None:
            return ErrorModel(**{'message': "User id {} not found".format(user_id)}), 404

        # Return data through schema model
        return UserModel(**user), 200


class GroupResource(Resource):
    post_parser = RequestParser()
    post_parser.add_argument('name', type=str, required="true")
    post_parser.add_argument('id', type=int, help='Id of new group')
    post_parser.add_argument('type', type=str, choices=['first', 'second', 'third'])
    added_groups = []

    @swagger.tags('groups')
    @swagger.response(response_code=201, description='created group')
    @swagger.reqparser(name='GroupsModel', parser=post_parser)
    def post(self):
        """
        Creates group
        """
        args = self.post_parser.parse_args()
        new_group = {'name': args['name'], 'id': len(self.added_groups) + 1}
        self.added_groups.append(new_group)

        return new_group, 201
