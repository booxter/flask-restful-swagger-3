#!/usr/bin/env python

# NOTE: Run with PYTHONPATH=. python example/app.py

from flask import Flask
from flask_cors import CORS

from flask_restful_swagger_3 import Api, swagger, get_swagger_blueprint

from views import UserResource, UserItemResource, GroupResource, ProductResource


app = Flask(__name__)
CORS(app)

security = [
    {
        "api_key": []
    }
]

authorizations = {
    "apikey": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    }
}

servers = [{"url": "http://localhost:5001"}]
api = Api(app, version='5', servers=servers, title="APP")


def auth(api_key, endpoint, method):
    # Space for your fancy authentication. Return True if access is granted, otherwise False
    return True


swagger.auth = auth


SWAGGER_URL = '/api/doc'  # URL for exposing Swagger UI (without trailing '/')
API_URL = 'swagger.json'  # Our API url (can of course be a local resource)

swagger_blueprint = get_swagger_blueprint(
    api.open_api_object,
    swagger_prefix_url=SWAGGER_URL,
    swagger_url=API_URL,
    authorizations=authorizations)


swagger.auth = auth

api.add_resource(UserResource, '/users')
api.add_resource(UserItemResource, '/users/<int:user_id>')
api.add_resource(GroupResource, '/groups')
api.add_resource(ProductResource, '/products')

app.register_blueprint(swagger_blueprint)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
