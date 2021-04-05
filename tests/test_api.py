import copy
import json
import pytest
from flask import Blueprint
from tests.base_test import BaseTest, BaseTestApi, NotAuthorizeApi, BaseTestApiBlueprint, BaseTestApiNoContext
from flask_restful_swagger_3 import swagger, get_swagger_blueprint, Api, Resource


class TestApi(BaseTestApi):

    def test_get_spec_object(self):
        # Retrieve spec object
        spec = self.api.open_api_object
        assert "info" in spec
        assert "title" in spec["info"]
        assert spec["info"]["title"] == "Example"
        assert 'paths' in spec
        assert 'parameters' in spec['paths']['/parse']['get']
        assert spec['openapi'] == '3.0.2'

    def test_get_spec(self):
        # Retrieve spec
        r = self.client_app.get('api/doc/swagger.json')
        assert r.status_code == 200

        data = json.loads(r.data.decode())
        assert 'info' in data
        assert 'paths' in data
        assert data['openapi'] == '3.0.2'
        assert data['paths']['/some_data']['get']['tags'] == ['Some data']

    def test_parse_query_parameters(self):
        r = self.client_app.get('/parse?str=Test' +
                             '&date=2016-01-01' +
                             '&datetime=2016-01-01T12:00:00%2B00:00' +
                             '&bool=False' +
                             '&int=123' +
                             '&float=1.23')

        assert r.status_code == 200

        data = json.loads(r.data.decode())
        assert data['str'] == 'Test'
        assert data['date'] == '2016-01-01T00:00:00'
        assert data['datetime'] == '2016-01-01T12:00:00+00:00'
        assert not data['bool']
        assert data['int'] == 123
        assert data['float'] == 1.23
        assert data['parsing'] == "testing"

    def test_parse_query_parameters_with_parsing_schema(self):
        r = self.client_app.get('/parse?str=Test' +
                                '&date=2016-01-01' +
                                '&datetime=2016-01-01T12:00:00%2B00:00' +
                                '&bool=False' +
                                '&int=123' +
                                '&float=1.23' +
                                '&parsing=some%20data')

        assert r.status_code == 200

        data = json.loads(r.data.decode())
        assert data['str'] == 'Test'
        assert data['date'] == '2016-01-01T00:00:00'
        assert data['datetime'] == '2016-01-01T12:00:00+00:00'
        assert not data['bool']
        assert data['int'] == 123
        assert data['float'] == 1.23
        assert data['parsing'] == "some data"

    def test_get_user(self):
        # Retrieve user
        r = self.client_app.get('/users/1?name=test')
        assert r.status_code == 200

        data = json.loads(r.data.decode())
        assert data['id'] == 1
        assert data['name'] == 'test'

    def test_post_user_with_swagger_payload(self):
        user_payload = {
            'id': 1,
            'name': 'fake_name'
        }
        r = self.client_app.post(
            "/users", data=json.dumps(user_payload), content_type="application/json"
        )
        assert r.status_code == 201

        data = json.loads(r.data.decode())
        assert data == {
            'id': 1,
            'name': 'fake_name'
        }

    def test_with_parser(self):
        user_payload = {
            'id': 2,
            'name': 'fake_name',
            'private': True
        }
        r = self.client_app.post(
            "/entities", data=json.dumps(user_payload), content_type="application/json"
        )
        assert r.status_code == 200

        data = json.loads(r.data.decode())
        assert data == {
            'id': 2,
            'name': 'fake_name'
        }

    def test_delete_user_return_no_content(self):
        r = self.client_app.get('api/doc/swagger.json')
        assert r.status_code == 200
        data = json.loads(r.data.decode())
        assert 'content' not in data['paths']['/users/{user_id}']['delete']['responses']['204']

    def test_resource_reqbody_reqparser_should_not_validate(self, bad_format_resource):
        with pytest.raises(swagger.ValidationError):
            self.api.add_resource(bad_format_resource, '/bad_resource')

    def test_bad_url_format(self, bad_format_url):
        with pytest.raises(swagger.ValidationError) as e:
            self.api.add_resource(bad_format_url, '/bad_url/')

        assert str(e.value) == "paths must not have ending slash"

    def test_two_much_converter_in_url(self, bad_format_url):
        with pytest.raises(ValueError) as e:
            self.api.add_resource(bad_format_url, '/bad_url/<string:email:test>')

        assert str(e.value) == "You must define one converter for a variable_name, " \
                               "if you want several converter don't mention any 'string:email'"

    def test_no_converter_in_url(self, no_converter_resource):
        self.api.add_resource(no_converter_resource, '/no_converter/<id>')

    def test_bad_schema_resource_in_parameters(self, bad_schema_resource_in_parameters):
        with pytest.raises(swagger.ValidationError) as e:
            self.api.add_resource(bad_schema_resource_in_parameters, '/url')

        assert str(e.value) == "'schema' must be of type 'dict' or subclass of 'Schema', not <class 'str'>"

    def test_bad_resource_parameter_type(self, bad_resource_parameter_type):
        with pytest.raises(ValueError) as e:
            bad_resource_parameter_type()

        assert str(e.value) == "'param' test must be of type 'dict'"

    def test_bad_resource_parameters_type(self, bad_resource_parameters_type):
        with pytest.raises(ValueError) as e:
            bad_resource_parameters_type()

    def test_bad_resource_parameters_in_is_path(self, bad_resource_parameters_in_is_path):
        with pytest.raises(swagger.ValidationError):
            bad_resource_parameters_in_is_path()

    def test_bad_schema_resource(self):
        class BadSchema:
            pass

        class SomeResource(Resource):
            @swagger.reorder_with(BadSchema, description="fake")
            def get(self):
                pass

        with pytest.raises(TypeError) as e:
            self.api.add_resource(SomeResource, '/url')

        assert str(e.value) == "'schema' used with 'reorder_with' must be a sub class of Schema"

        class SomeResource(Resource):
            @swagger.reorder_with({'id': {'type': 'int'}}, description="fake")
            def get(self):
                pass

        with pytest.raises(TypeError) as e:
            self.api.add_resource(SomeResource, '/url')

        assert str(e.value) == "'schema' used with 'reorder_with' must be a sub class of Schema"

    def test_expected_with_none(self):

        class SomeResource(Resource):
            @swagger.response(response_code=201, description="create something")
            @swagger.expected(None)
            def post(self):
                return None

        self.api.add_resource(SomeResource, '/url')

    def test_get_swagger_blueprint(self):
        swagger_blueprint = get_swagger_blueprint(self.api.open_api_object, swagger_blueprint_name="swagger_app")
        self.app.register_blueprint(swagger_blueprint)
        swagger_ui_result = self.client_app.get('/')
        assert swagger_ui_result.status_code == 200

        swagger_bundle = self.client_app.get('/swagger-ui-bundle.js')
        assert swagger_bundle.status_code == 200

        swagger_standalone = self.client_app.get('/swagger-ui-standalone-preset.js')
        assert swagger_standalone.status_code == 200

        swagger_css = self.client_app.get('/swagger-ui.css')
        assert swagger_css.status_code == 200

        spec_result = self.client_app.get('/api/doc/swagger.json')
        assert spec_result.status_code == 200

        spec = json.loads(spec_result.data.decode())
        assert spec['openapi'] == '3.0.2'
        assert 'info' in spec
        assert 'paths' in spec

    def test_get_swagger_blueprint_with_url_prefix(self):
        self.app.config.setdefault('SWAGGER_BLUEPRINT_URL_PREFIX', '/my_swagger')
        with self.ctx:
            swagger_blueprint = get_swagger_blueprint(self.api.open_api_object,
                                                      swagger_blueprint_name="swagger_app_with_url_prefix")
        self.app.register_blueprint(swagger_blueprint)
        swagger_ui_result = self.client_app.get('/')
        assert swagger_ui_result.status_code == 200

        swagger_bundle = self.client_app.get('/swagger-ui-bundle.js')
        assert swagger_bundle.status_code == 200

        swagger_standalone = self.client_app.get('/swagger-ui-standalone-preset.js')
        assert swagger_standalone.status_code == 200

        swagger_css = self.client_app.get('/swagger-ui.css')
        assert swagger_css.status_code == 200

        spec_result = self.client_app.get('/api/doc/swagger.json')
        assert spec_result.status_code == 200

        spec = json.loads(spec_result.data.decode())
        assert spec['openapi'] == '3.0.2'
        assert 'info' in spec
        assert 'paths' in spec

    def test_other(self):
        r = self.client_app.post('/api/users?id=0&name=string&mail=john.doe@butcher.com&keys=john&keys=max')
        data = json.loads(r.data.decode())
        expected = {'id': 0, 'name': 'string', 'mail': 'john.doe@butcher.com', 'keys': ['john', 'max']}
        assert r.status_code == 201
        assert data == expected

    def test_request_parser_spec_definitions(self):
        # Retrieve spec
        r = self.client_app.get('/api/doc/swagger.json')
        assert r.status_code == 200

        data = json.loads(r.data.decode())
        assert 'components' in data
        assert 'schemas' in data['components']
        assert 'EntityAddParser' in data['components']['schemas']
        assert data['components']['schemas']['EntityAddParser']['type'] == 'object'

        properties = data['components']['schemas']['EntityAddParser']['properties']
        required = data['components']['schemas']['EntityAddParser']['required']

        id_prop = properties.get('id')
        assert id_prop
        assert 'default' not in id_prop
        assert 'id' not in required
        assert id_prop['type'] == 'integer'
        assert id_prop['description'] == 'id help'

        name_prop = properties.get('name')
        assert name_prop
        assert 'default' not in name_prop
        assert 'name' not in required
        assert name_prop['type'] == 'string'
        assert 'description' not in name_prop

        priv_prop = properties.get('private')
        assert priv_prop
        assert 'default' not in priv_prop
        assert 'private' in required
        assert priv_prop['type'] == 'boolean'
        assert 'description' not in priv_prop

        val_prop = properties.get('value')
        assert val_prop
        assert val_prop['default'] == 1.1
        assert 'value' not in required
        assert val_prop['type'] == 'float'
        assert 'description' not in val_prop

        assert properties.get('password_arg')
        assert properties['password_arg']['type'] == 'password'


class TestApiNoContext(BaseTestApiNoContext):
    def test_get_swagger_blueprint(self):
        blueprint = get_swagger_blueprint(self.api.open_api_object, swagger_blueprint_name="swagger_app")
        self.app.register_blueprint(blueprint)
        swagger_ui_result = self.client_app.get('/')
        assert swagger_ui_result.status_code == 200

        swagger_bundle = self.client_app.get('/swagger-ui-bundle.js')
        assert swagger_bundle.status_code == 200

        swagger_standalone = self.client_app.get('/swagger-ui-standalone-preset.js')
        assert swagger_standalone.status_code == 200

        swagger_css = self.client_app.get('/swagger-ui.css')
        assert swagger_css.status_code == 200

        spec_result = self.client_app.get('/api/doc/swagger.json')
        assert spec_result.status_code == 200

        spec = json.loads(spec_result.data.decode())
        assert spec['openapi'] == '3.0.2'
        assert 'info' in spec
        assert 'paths' in spec

    def test_get_swagger_blueprint_with_url_prefix_return_404_when(self):
        blueprint = get_swagger_blueprint(self.api.open_api_object)
        self.app.register_blueprint(blueprint, url_prefix="/my_swagger")
        swagger_ui_result = self.client_app.get('/my_swagger')
        assert swagger_ui_result.status_code == 200

        swagger_bundle = self.client_app.get('/my_swagger/swagger-ui-bundle.js')
        assert swagger_bundle.status_code == 200

        swagger_standalone = self.client_app.get('/my_swagger/swagger-ui-standalone-preset.js')
        assert swagger_standalone.status_code == 200

        swagger_css = self.client_app.get('/my_swagger/swagger-ui.css')
        assert swagger_css.status_code == 200

        spec_result = self.client_app.get('/my_swagger/api/doc/swagger.json')
        assert spec_result.status_code == 200

        spec = json.loads(spec_result.data.decode())
        assert spec['openapi'] == '3.0.2'
        assert 'info' in spec
        assert 'paths' in spec


class TestBlueprint(BaseTest):
    @pytest.fixture(autouse=True)
    def init_blueprint(self, user_secured_resource, partial_secured_resource):
        self.authorizations = {
            "apikey": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
        self.blueprint = Blueprint('other', __name__)
        self.api = Api(self.blueprint, add_api_spec_resource=False, authorizations=self.authorizations)
        self.api.add_resource(user_secured_resource, '/users')
        self.api.add_resource(partial_secured_resource, '/partial')

    def test_get_spec_object(self):
        # Retrieve spec object
        spec = self.api.open_api_object

        assert "info" in spec
        assert "title" in spec["info"]
        assert spec["info"]["title"] == "Example"
        assert 'paths' in spec
        assert 'parameters' in spec['paths']['/users']['get']
        assert '/partial' in spec['paths']
        assert spec['openapi'] == '3.0.2'
        assert spec['components']['securitySchemes'] == self.authorizations

    def test_get_spec_object_from_url_should_return_404(self):
        r = self.client_app.get('/api/doc/swagger.json')
        assert r.status_code == 404

    def test_get_swagger_blueprint(self):
        swagger_blueprint = get_swagger_blueprint(self.api.open_api_object, swagger_blueprint_name="swagger_app")
        self.app.register_blueprint(swagger_blueprint)
        swagger_ui_result = self.client_app.get('/')
        assert swagger_ui_result.status_code == 200

        swagger_bundle = self.client_app.get('/swagger-ui-bundle.js')
        assert swagger_bundle.status_code == 200

        swagger_standalone = self.client_app.get('/swagger-ui-standalone-preset.js')
        assert swagger_standalone.status_code == 200

        swagger_css = self.client_app.get('/swagger-ui.css')
        assert swagger_css.status_code == 200

        spec_result = self.client_app.get('/api/doc/swagger.json')
        assert spec_result.status_code == 200
        spec = json.loads(spec_result.data.decode())
        assert spec['openapi'] == '3.0.2'
        assert 'info' in spec
        assert 'paths' in spec

    def test_get_swagger_blueprint_with_url_prefix(self):
        self.app.config.setdefault('SWAGGER_BLUEPRINT_URL_PREFIX', '/my_swagger')
        with self.ctx:
            swagger_blueprint = get_swagger_blueprint(self.api.open_api_object, swagger_blueprint_name="swagger_app_with_url_prefix")
        self.app.register_blueprint(swagger_blueprint, url_prefix="/my_swagger")
        swagger_ui_result = self.client_app.get('/my_swagger')
        assert swagger_ui_result.status_code == 200

        swagger_bundle = self.client_app.get('/my_swagger/swagger-ui-bundle.js')
        assert swagger_bundle.status_code == 200

        swagger_standalone = self.client_app.get('/my_swagger/swagger-ui-standalone-preset.js')
        assert swagger_standalone.status_code == 200

        swagger_css = self.client_app.get('/my_swagger/swagger-ui.css')
        assert swagger_css.status_code == 200

        spec_result = self.client_app.get('/my_swagger/api/doc/swagger.json')
        assert spec_result.status_code == 200
        spec = json.loads(spec_result.data.decode())
        assert spec['openapi'] == '3.0.2'
        assert 'info' in spec
        assert 'paths' in spec

    def test_bad_blueprint_url(self, user_resource):
        self.blueprint = Blueprint('user', __name__, url_prefix="test")
        self.api = Api(self.blueprint, add_api_spec_resource=False)

        with pytest.raises(swagger.ValidationError) as e:
            self.api.add_resource(user_resource, '/users')

        assert str(e.value) == "url_prefix must start with a leading slash"

        self.blueprint = Blueprint('user', __name__, url_prefix="/test/")
        self.api = Api(self.blueprint, add_api_spec_resource=False)

        with pytest.raises(swagger.ValidationError) as e:
            self.api.add_resource(user_resource, '/users')

        assert str(e.value) == "url_prefix must not have ending slash"


class TestBlueprintWithUrlPrefix(BaseTestApiBlueprint):
    def test_blueprint_url(self):
        swagger_blueprint = get_swagger_blueprint(self.api.open_api_object)
        self.app.register_blueprint(swagger_blueprint)
        swagger_ui_result = self.client_app.get('/')
        assert swagger_ui_result.status_code == 200

        swagger_bundle = self.client_app.get('/swagger-ui-bundle.js')
        assert swagger_bundle.status_code == 200

        swagger_standalone = self.client_app.get('/swagger-ui-standalone-preset.js')
        assert swagger_standalone.status_code == 200

        swagger_css = self.client_app.get('/swagger-ui.css')
        assert swagger_css.status_code == 200

        spec_result = self.client_app.get('/api/doc/swagger.json')
        assert spec_result.status_code == 200
        spec = json.loads(spec_result.data.decode())
        assert spec['openapi'] == '3.0.2'
        assert 'info' in spec
        assert 'paths' in spec
        assert '/api/users/{user_id}' in spec['paths']

        r = self.client_app.get('/api/users/1?name=test')
        assert r.status_code == 200
        data = json.loads(r.data.decode())
        assert data == {'id': 1, 'name': 'test'}


class TestBlueprintUpdateAuthorizations(BaseTest):
    @pytest.fixture(autouse=True)
    def init_blueprint(self, user_resource):
        self.authorizations = {
            "http": {
                "type": "http",
                "scheme": "basic"
            }
        }
        self.blueprint = Blueprint('other', __name__)
        self.api = Api(self.blueprint, add_api_spec_resource=False, authorizations=self.authorizations)
        self.api.add_resource(user_resource, '/users')

    def test_get_swagger_blueprint_with_authorizations(self):
        swagger_blueprint = get_swagger_blueprint(
            self.api.open_api_object,
            swagger_blueprint_name="swagger_app_with_authorizations"
        )
        self.app.register_blueprint(swagger_blueprint)
        swagger_ui_result = self.client_app.get('/')
        assert swagger_ui_result.status_code == 200

        swagger_bundle = self.client_app.get('/swagger-ui-bundle.js')
        assert swagger_bundle.status_code == 200

        swagger_standalone = self.client_app.get('/swagger-ui-standalone-preset.js')
        assert swagger_standalone.status_code == 200

        swagger_css = self.client_app.get('/swagger-ui.css')
        assert swagger_css.status_code == 200

        spec_result = self.client_app.get('/api/doc/swagger.json')
        assert spec_result.status_code == 200
        spec = json.loads(spec_result.data.decode())
        assert spec['openapi'] == '3.0.2'
        assert 'info' in spec
        assert 'paths' in spec
        expected_authorizations = copy.deepcopy(self.authorizations)
        assert spec['components']['securitySchemes'] == expected_authorizations


class TestNoAuthorizeApi(NotAuthorizeApi):

    def test_get_spec_object(self):
        # Retrieve spec object
        spec = self.api.open_api_object
        assert "info" in spec
        assert "title" in spec["info"]
        assert spec["info"]["title"] == "Example"
        assert 'paths' in spec
        assert 'parameters' in spec['paths']['/parse']['get']
        assert spec['openapi'] == '3.0.2'

    def test_get_spec(self):
        # Retrieve spec
        r = self.client_app.get('api/doc/swagger.json')
        assert r.status_code == 200

        data = json.loads(r.data.decode())
        assert 'info' in data
        assert 'paths' in data
        assert data['openapi'] == '3.0.2'
        assert data['paths'] == {}

    def test_parse_query_parameters(self):
        r = self.client_app.get('/parse?str=Test' +
                             '&date=2016-01-01' +
                             '&datetime=2016-01-01T12:00:00%2B00:00' +
                             '&bool=False' +
                             '&int=123' +
                             '&float=1.23')

        assert r.status_code == 401

        data = json.loads(r.data.decode())
        assert data == {
            'message': "The server could not verify that you are authorized to access the URL requested. " +
            "You either supplied the wrong credentials (e.g. a bad password), " +
            "or your browser doesn't understand how to supply the credentials required."
        }
