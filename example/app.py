#!/usr/bin/env python

# NOTE: Run with PYTHONPATH=. python example/app.py

from flask import Flask, url_for
from flask_cors import CORS
from flask_restful_swagger_3 import Api, swagger
from flask_swagger_ui import get_swaggerui_blueprint

from views import UserResource, UserItemResource, GroupResource


app = Flask(__name__)
CORS(app)

servers = [{"url": "http://localhost:5000"}]
api = Api(app, version='5', servers=servers, title="APP")


def auth(api_key, endpoint, method):
    # Space for your fancy authentication. Return True if access is granted, otherwise False
    return True


swagger.auth = auth


SWAGGER_URL = '/api/doc'  # URL for exposing Swagger UI (without trailing '/')
API_URL = 'swagger.json'  # Our API url (can of course be a local resource)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL
)


swagger.auth = auth

api.add_resource(UserResource, '/api/users')
api.add_resource(UserItemResource, '/api/users/<int:user_id>')
api.add_resource(GroupResource, '/api/groups/')

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
