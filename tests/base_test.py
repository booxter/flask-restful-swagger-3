from flask import Flask, Blueprint
from flask_restful_swagger_3 import Api, swagger
from tests.fixtures.fixture_resources import parse_resource, user_resource, entity_add_resource, p_resource, one_resource


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


class BaseTestApi:
    app = None
    api = None
    client_app = None

    @classmethod
    def setup_class(cls):
        app = Flask(__name__)
        app.testing = True

        cls.app = app
        cls.api = Api(cls.app)
        cls.api.add_resource(parse_resource(), '/parse')
        cls.api.add_resource(user_resource(), '/users/<int:user_id>')
        cls.api.add_resource(entity_add_resource(), '/entities')
        cls.api.add_resource(p_resource(), '/api/users')
        cls.api.add_resource(one_resource(), '/some_data')
        cls.ctx = app.app_context()
        cls.ctx.push()
        cls.client_app = app.test_client()

    @classmethod
    def teardown_class(cls):
        cls.ctx.pop()


class BaseTestApiNoContext:
    app = None
    api = None
    client_app = None

    @classmethod
    def setup_class(cls):
        app = Flask(__name__)
        app.testing = True

        cls.app = app
        cls.api = Api(cls.app)
        cls.api.add_resource(parse_resource(), '/parse')
        cls.client_app = app.test_client()


class BaseTestApiBlueprint:
    app = None
    api = None
    blueprint = None
    client_app = None

    @classmethod
    def setup_class(cls):
        app = Flask(__name__)
        app.testing = True

        cls.app = app
        cls.blueprint = Blueprint('user', __name__, url_prefix='/api')
        cls.api = Api(cls.blueprint)
        cls.api.add_resource(user_resource(), '/users/<int:user_id>')
        cls.app.register_blueprint(cls.blueprint)
        cls.ctx = app.app_context()
        cls.ctx.push()
        cls.client_app = app.test_client()

    @classmethod
    def teardown_class(cls):
        cls.ctx.pop()


class NotAuthorizeApi:
    app = None
    api = None
    client_app = None

    @classmethod
    def setup_class(cls):
        app = Flask(__name__)
        app.testing = True

        def auth(api_key, endpoint, method):
            return False

        swagger.auth = auth

        cls.app = app
        cls.api = Api(cls.app)
        cls.api.add_resource(parse_resource(), '/parse')
        cls.api.add_resource(user_resource(), '/users/<int:user_id>')
        cls.api.add_resource(p_resource(), '/api/users')
        cls.api.add_resource(one_resource(), '/some_data')
        cls.ctx = app.app_context()
        cls.ctx.push()
        cls.client_app = app.test_client()

    @classmethod
    def teardown_class(cls):
        cls.ctx.pop()
