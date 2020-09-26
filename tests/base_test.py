from flask import Flask
from flask_restful_swagger_3 import Api
from tests.fixtures.fixture_resources import ParseResource, UserResource, EntityAddResource, PResource


class BaseTest:
    app = None
    client_app = None

    @classmethod
    def setup_class(cls):
        app = Flask(__name__)
        app.testing = True

        cls.app = app
        cls.ctx = app.app_context()
        cls.ctx.push()
        cls.client_app = app.test_client()

    @classmethod
    def teardown_class(cls):
        cls.ctx.pop()


class BaseTestapi:
    app = None
    api = None
    client_app = None

    @classmethod
    def setup_class(cls):
        app = Flask(__name__)
        app.testing = True

        cls.app = app
        cls.api = Api(cls.app, )
        cls.api.add_resource(ParseResource, '/parse')
        cls.api.add_resource(UserResource, '/users/<int:user_id>')
        cls.api.add_resource(EntityAddResource, '/entities/')
        cls.api.add_resource(PResource, '/api/users')
        cls.ctx = app.app_context()
        cls.ctx.push()
        cls.client_app = app.test_client()

    @classmethod
    def teardown_class(cls):
        cls.ctx.pop()
