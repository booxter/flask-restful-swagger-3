import json
import werkzeug
import pytest
from flask_restful_swagger_3 import Api, swagger, Blueprint, abort, get_swagger_blueprint
from tests.resources import UserResource, EntityAddResource, ParseResource


def test_get_swagger_blueprint(test_app):
    with test_app["context"]:
        docs = []
        spec = test_app["api"].get_swagger_doc()
        docs.append(spec)
        servers = [{"url": "http://localhost:5000"}]
        assert get_swagger_blueprint(docs, "/api/swagger", title='Example', version='1', servers=servers)


def test_get_spec_object(test_app):
    with test_app["context"]:
        spec = test_app["api"].get_swagger_doc()
        assert "info" in spec
        assert 'paths' in spec
        assert 'parameters' in spec['paths']['/parse']['get']
        assert spec['openapi'] == '3.0.0'


def test_api_failed(test_app_flask):
    api = Api(test_app_flask)
    with pytest.raises(swagger.ValidationError):
        api.add_resource(ParseResource, 'parse')


def test_blueprint_failed():
    blueprint = Blueprint('parser', __name__, url_prefix="v1")
    api = Api(blueprint, add_api_spec_resource=False)
    with pytest.raises(swagger.ValidationError):
        api.add_resource(ParseResource, '/parser')

    blueprint = Blueprint('parser', __name__, url_prefix="/v1/")
    api = Api(blueprint, add_api_spec_resource=False)
    with pytest.raises(swagger.ValidationError):
        api.add_resource(ParseResource, '/parser')


def test_blueprint():
    blueprint = Blueprint('parser', __name__, url_prefix="/v1")
    api = Api(blueprint, add_api_spec_resource=False)
    api.add_resource(ParseResource, '/parser')


def test_get_spec(test_app):
    # Retrieve spec
    r = test_app["app"].get('/api/swagger.json')
    assert r.status_code == 200

    data = json.loads(r.data.decode('utf-8'))
    assert 'info' in data
    assert 'paths' in data
    assert data['openapi'] == '3.0.0'


def test_abort(test_app):
    r = test_app["app"].get('/api/not_exists')
    if r .status_code != 200:
        with pytest.raises(werkzeug.exceptions.BadRequest):
            abort(400, schema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                }
            })


def test_request_parser_spec_definitions(test_parser):
    # Retrieve spec
    r = test_parser["app"].get('/api/swagger.json')
    assert r.status_code == 200

    data = json.loads(r.data.decode('utf-8'))
    assert 'responses' in data['paths']["/entities/"]["post"]
    assert 'EntityAddParser' in data['components']['schemas']
    assert data['components']['schemas']['EntityAddParser']['type'] == 'object'

    properties = data['components']['schemas']['EntityAddParser']['properties']
    id_prop = properties.get('id')
    assert id_prop is not None
    assert 'default' not in id_prop
    assert not id_prop['required']
    assert id_prop['type'] == 'integer'
    assert id_prop['name'] == 'id'
    assert id_prop['description'] == 'id help'

    name_prop = properties.get('name')
    assert name_prop is not None
    assert 'default' not in name_prop
    assert not name_prop['required']
    assert name_prop['type'] == 'string'
    assert name_prop['name'] == 'name'
    assert name_prop['description'] is None

    priv_prop = properties.get('private')
    assert priv_prop is not None
    assert 'default' not in priv_prop
    assert priv_prop['required']
    assert priv_prop['type'] == 'boolean'
    assert priv_prop['name'] == 'private'
    assert priv_prop['description'] is None

    val_prop = properties.get('value')
    assert val_prop is not None
    assert val_prop['default'] == 1.1
    assert not val_prop['required']
    assert val_prop['type'] == 'number'
    assert val_prop['name'] == 'value'
    assert val_prop['description'] is None

    assert properties.get('password_arg') is not None
    assert properties['password_arg']['type'] == 'password'
