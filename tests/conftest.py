import pytest
from flask import Flask
from flask_restful_swagger_3 import Api
from tests.resources import UserResource, EntityAddResource, ParseResource


@pytest.fixture(scope="module")
def test_app():
    flask_app = Flask(__name__)
    api = Api(flask_app)
    api.add_resource(ParseResource, '/parse')
    api.add_resource(UserResource, '/users/<int:user_id>')
    app = flask_app.test_client()
    context = flask_app.test_request_context()
    yield {"app": app, "api": api, "context": context}


@pytest.fixture(scope="module")
def test_app_flask():
    flask_app = Flask(__name__)
    yield flask_app


@pytest.fixture(scope="module")
def test_api():
    flask_app = Flask(__name__)
    api = Api(flask_app)
    yield api


@pytest.fixture(scope="module")
def test_parser():
    flask_app = Flask(__name__)
    api = Api(flask_app)
    api.add_resource(EntityAddResource, '/entities/')
    app = flask_app.test_client()
    context = flask_app.test_request_context()
    yield {"app": app, "api": api, "context": context}
