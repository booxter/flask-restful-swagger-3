import json
import pytest
from flask import Blueprint
from tests.base_test import BaseTest, BaseTestapi
from tests.fixtures.fixture_resources import BadFormatResourceReqbodyReqparser, BadFormatUrl, UserResource
from flask_restful_swagger_3 import swagger, get_swagger_blueprint, Api


class TestApi(BaseTestapi):

    def test_get_spec_object(self):
        # Retrieve spec object
        spec = self.api.open_api_json
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

    def test_get_user(self):
        # Retrieve user
        r = self.client_app.get('/users/1?name=test')
        assert r.status_code == 200

        data = json.loads(r.data.decode())
        assert data['id'] == 1
        assert data['name'] == 'test'

    def test_delete_user_return_no_content(self):
        r = self.client_app.get('api/doc/swagger.json')
        assert r.status_code == 200
        data = json.loads(r.data.decode())
        assert 'content' not in data['paths']['/users/{user_id}']['delete']['responses']['204']

    def test_resource_reqbody_reqparser_should_not_validate(self):
        with pytest.raises(swagger.ValidationError):
            self.api.add_resource(BadFormatResourceReqbodyReqparser, '/bad_resource')

    def test_bad_url_format(self):
        with pytest.raises(ValueError):
            self.api.add_resource(BadFormatUrl, 'bad_url')

        with pytest.raises(ValueError):
            self.api.add_resource(BadFormatUrl, 'bad_url/')

    def test_get_swagger_blueprint(self):
        swagger_blueprint = get_swagger_blueprint(self.api.open_api_json, swagger_blueprint_name="swagger_app")
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
        blueprint = get_swagger_blueprint(self.api.open_api_json)
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

    def test_other(self):
        r = self.client_app.post('/api/users?id=0&name=string&mail=john.doe@butcher.com&keys=john&keys=max')
        data = json.loads(r.data.decode())
        expected = {'id': 0, 'name': 'string', 'mail': 'john.doe@butcher.com', 'keys': ['john', 'max']}
        assert r.status_code == 201
        assert data == expected


class TestFlaskSwaggerRequestParser(BaseTestapi):

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


class TestBlueprint(BaseTest):
    def setup_method(self):
        self.blueprint = Blueprint('user', __name__)
        self.api = Api(self.blueprint, '/test', add_api_spec_resource=False)
        self.api.add_resource(UserResource, '/users')

    def test_get_spec_object(self):
        # Retrieve spec object
        spec = self.api.open_api_json

        assert "info" in spec
        assert "title" in spec["info"]
        assert spec["info"]["title"] == "Example"
        assert 'paths' in spec
        assert 'parameters' in spec['paths']['/users']['get']
        assert spec['openapi'] == '3.0.2'

    def test_get_spec_object_from_url_should_return_404(self):
        r = self.client_app.get('/api/doc/swagger.json')
        assert r.status_code == 404

    def test_get_swagger_blueprint(self):
        swagger_blueprint = get_swagger_blueprint(self.api.open_api_json, swagger_blueprint_name="swagger_app")
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
            swagger_blueprint = get_swagger_blueprint(self.api.open_api_json, swagger_blueprint_name="swagger_app_with_url_prefix")
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
