#!/usr/bin/env python

# NOTE: Run with PYTHONPATH=. python example/app.py

from flask import Flask
from flask_cors import CORS
from flask_restful_swagger_3 import Api, swagger, get_swagger_blueprint

from views import UserResource, UserItemResource, GroupResource


app = Flask(__name__)
CORS(app)

servers = [{"url": "http://localhost:5000"}]
api = Api(app, version='5', servers=servers, title="APP", add_api_spec_resource=False)


def auth(api_key, endpoint, method):
    # Space for your fancy authentication. Return True if access is granted, otherwise False
    return True


swagger.auth = auth


SWAGGER_URL = '/api/doc'  # URL for exposing Swagger UI (without trailing '/')
API_URL = 'swagger.json'  # Our API url (can of course be a local resource)

app.config.setdefault('SWAGGER_BLUEPRINT_URL_PREFIX', '/swagger')
swagger_blueprint_url_prefix = app.config.get('SWAGGER_BLUEPRINT_URL_PREFIX', '')

with app.app_context():
    swagger_blueprint = get_swagger_blueprint(
        api.open_api_json,
        swagger_prefix_url=SWAGGER_URL,
        swagger_url=API_URL,
        title='Example', version='1', servers=servers)


swagger.auth = auth

api.add_resource(UserResource, '/api/users')
api.add_resource(UserItemResource, '/api/users/<int:user_id>')
api.add_resource(GroupResource, '/api/groups/')

app.register_blueprint(swagger_blueprint, url_prefix=swagger_blueprint_url_prefix)
# use can also use app.register_blueprint(swagger_blueprint, url_prefix='/swagger')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
