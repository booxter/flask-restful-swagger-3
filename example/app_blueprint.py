#!/usr/bin/env python

# NOTE: Run with PYTHONPATH=. python example/app.py

from flask import Flask, current_app
from flask_cors import CORS
from flask_restful_swagger_3 import swagger, get_swagger_blueprint
from flask_swagger_ui import get_swaggerui_blueprint

from views_blueprint import get_user_resources

app = Flask(__name__)
CORS(app, resources={"/api/*": {"origins": "*"}})


def auth(api_key, endpoint, method):
    # Space for your fancy authentication. Return True if access is granted, otherwise False
    return True


swagger.auth = auth

# Get user resources
user_resources = get_user_resources()

# Register the blueprint for user resources
app.register_blueprint(user_resources.blueprint)

# Prepare a blueprint to server the combined list of swagger document objects and register it
servers = [{"url": "http://localhost:5001"}]


SWAGGER_URL = '/api'  # URL for exposing Swagger UI (without trailing '/')
API_URL = 'swagger.json'  # Our API url (can of course be a local resource)

app.register_blueprint(get_swagger_blueprint(user_resources.open_api_json, "/api/swagger", title='Example', version='1', servers=servers))

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5001')
