# flask-restful-swagger-3


## What is flask-restful-swagger-3?

flask-restful-swagger-3 is a wrapper for [flask-restful](http://flask-restful.readthedocs.org/en/latest/) which
enables [swagger3](http://swagger.io/) support according to the [openapi 3.0.0 specification](https://swagger.io/specification/).

This project is based on [flask-restful-swagger-2](https://github.com/soerface/flask-restful-swagger-2.0), but it only
supported swagger 2.0.

## Getting started

Install:

```
pip install flask-restful-swagger-3
```

To use it, change your import from `from flask_restful import Api` to `from flask_restful_swagger_3 import Api`.

```python
from flask import Flask
# Instead of using this: from flask_restful import Api
# Use this:
from flask_restful_swagger_3 import Api

app = Flask(__name__)

# Use the swagger Api class as you would use the flask restful class.
# It supports several (optional) parameters, these are the defaults:
api = Api(app)
```

The Api class supports the following parameters:

| Parameter | Description |
| --------- | ----------- |
| `add_api_spec_resource` | Set to `True` to add an endpoint to serve the swagger specification (defaults to `True`). |
| `version` | The API version string (defaults to '0.0'). Maps to the `version` field of the [info object](https://swagger.io/specification/#infoObject). |
| `swagger_prefix_url` | The URL prefix for swagger (defaults to `/api/doc)` |
| `swagger_url`| The URL path that serves the swagger specification document (defaults to `swagger.json`). |
| `servers` | The list of server on which the API is served, it replaces `schemes`, `host` and `base_path`. Maps to the [server object](https://swagger.io/specification/#serverObject). |
| `components` | A list reusable objects for different aspects of the OAS. All objects defined within the components object will have no effect on the API unless they are explicitly referenced from properties outside the components object. Maps to the [components](http://swagger.io/specification/#componentsObject). |
| `contact` | The contact information for the API. Maps to the `contact` field of the [info object](https://swagger.io/specification/#infoObject). |
| `description` | A short description of the application. Maps to the `description` field of the [info object](https://swagger.io/specification/#infoObject). |
| `external_docs` | Additional external documentation. Maps to the `externalDocs` field of the [operation object](https://swagger.io/specification/#operationObject). |
| `license` | The license information for the API. Maps to the `license` field of the [info object](https://swagger.io/specification/#infoObject). |
| `parameters` | The parameters that can be used across operations. Maps to the `parameters` field of the [operation object](https://swagger.io/specification/#operationObject). |
| `security` | A declaration of which security mechanisms can be used across the API. The list of values includes alternative security requirement objects that can be used. Only one of the security requirement objects need to be satisfied to authorize a request. Individual operations can override this definition. Maps to the `security` field of the [OpenAPI Object](http://swagger.io/specification/#openapiObject). |
| `authorizations` | Defines a security scheme that can be used by the operations. Maps to the `securitySchemes` field of [components Object](https://swagger.io/specification/#componentsObject) |
| `tags` | A list of tags used by the specification with additional metadata. Maps to the `tags` field fo the [OpenAPI Object](https://swagger.io/specification/#openapiObject). |
| `terms` | The terms of service for the API. Maps to the `termsOfService` field of the [info object](https://swagger.io/specification/#infoObject). |
| `title` | The title of the application (defaults to the flask app module name). Maps to the `title` field of the [info object](https://swagger.io/specification/#infoObject). |

To see

## Documenting API endpoints

You can decorate your Api endpoiints with several decorators to build to swagger object:

#### List of decorators

_You need to import `swagger` from `flask_restful_swagger_3`_


* `swagger.tags`: Allow to group operations with a list of tags (argument accepted: a list of strings)
* `swagger.reorder_with`: Apply a schema and a response to a method, default response code is `200` (argument accepted: `schema`: the schema to apply, `as_list`: Apply the schema as list (default is `False`), `response_code`: The response code to apply the example schema (default is `200`), `description`: Description of the response code (default is the function doc), `summary`: Summary of the method (if setted in `response`, you don't need it here))
* `swagger.reorder_list_with`: Same as `swagger.reorder_with` with `as_list` at `True`
* `swagger.response`: Add a response to the method (argument accepted: `response_code`:  The response to add to the method, `description`: The description of the response, `schema`: The schema to apply to the method, `no_content`: if `True`: `content` is not added to response, default: `False`, `example`: example of response, `summary`: Summary of the method (if setted in `reorder_with` or `reorder_list_with`, you don't need it here))
* `swagger.parameter`: Add a parameter to the method (Don't use the `path`parameter, it will be added automatically with a url with variable: `/users:<int:user_id>`) (argument accepted: _in, name, schema, description or a `dictionnary)
* `swagger.parameters`: Add several parameters to the method, it can add the args to the `_parser` of the method if exist  (argument accepted: a list of parameter)
* `swagger.expected`: Add a request body to the method (argument accepted: `schema`: The schema expected, `required`)
* `swagger.reqparser`: Add  request body to the method using RequestParser (argument accepted: `name`: Name use to generate the model, `parser`: The RequestParser() object)
* `swagger.security`: Add security to a method or a resource. Each argument MUST correspond to a security scheme which is declared in the `Security Schemes` under the Components Object (declared by `authorizations` in Api instance)

```python
from flask_restful_swagger_3 import swagger, Resource


class UserItemResource(Resource):
    @swagger.tags(['user'])
    @swagger.reorder_with(UserModel, description="Returns a user", summary="Get User")
    def get(self, user_id):
        # Do some processing
        return UserModel(**{'id': 1, 'name': 'somebody'}), 200  # generates json response {"id": 1, "name": "somebody"}

```

Use add_resource as usual.

```python
api.add_resource(UserItemResource, '/api/users/<int:user_id>')
```

## Parsing query parameters

If a resource has decorator ``swagger.parameters`` or ``swagger.parameter`` with `in` or `_in` equal `query`, the
documentation will be automatically added to a reqparse parser and assigned to the `_parser` argument.

## Using models

Create a model by inheriting from `flask_restful_swagger_3.Schema`

```python
from flask_restful_swagger_3 import Schema


class EmailModel(Schema):
    type = 'string'
    format = 'email'


class KeysModel(Schema):
    type = 'object'
    properties = {
        'name': {
            'type': 'string'
        }
    }

class UserModel(Schema):
    properties = {
        'id': {
            'type': 'integer',
            'format': 'int64',
        },
        'name': {
            'type': 'string'
        },
        'mail': EmailModel,
        'keys': KeysModel.array(),
        'user_type': {
            'type': 'string',
            'enum': ['admin', 'regular'],
            'nullable': True
        },
        'password': {
            'type': 'string',
            'format': 'password',
            'load_only': True
        }
    }
    required = ['name']
```

For each ``properties``, you can add ``nullable``, ``dump_only`` and ``load_only`` (look ``UserModel`` example):

* ``nullable``: The property can be ``None`` (``null`` in json format)
* ``dump_only``: The schema will raise an error if property is added
* ``load_only``: The schema will not display the property

### SuperModel

You can create super model:

__WARNING__ :
* You can create only super model with type ``object``
* The inherited model must same type of super model (The best use is to not add type to inherited Schema)

```python
from flask_restful_swagger_3 import Schema

class PersonModel(Schema):
    type = 'object'
    properties = {
        'id': {
            'type': 'integer',
            'format': 'int64'
        },
        'name': {
            'type': 'string'
        }
    }

class EmployeeModel(PersonModel):
    properties = {
        'role': {
            'type': 'string'
        }
    }

employee_1 = {
    'id': 1,
    'name': 'john',
    'role': 'admin'
}

EmployeeModel(**employee_1) # will validate the object
```

You can build your models according to the [swagger schema object specification](http://swagger.io/specification/#schemaObject)

It is recommended that you always return a model in your views so that your code and documentation are in sync.

## RequestParser support

You can specify RequestParser object if you want to pass its arguments to spec. In such case, there is not need to define model manually

```python
from flask_restful.reqparse import RequestParser

from flask_restful_swagger_3 import swagger, Resource


class GroupResource(Resource):
    post_parser = RequestParser()
    post_parser.add_argument('name', type=str, required=True)
    post_parser.add_argument('id', type=int, help='Id of new group')

    @swagger.tags(['groups'])
    @swagger.response(response_code=201, description='created group')
    @swagger.reqparser(name='GroupsModel', parser=post_parser)
    def post(self):
    ...
```

Swagger schema (among other things):

```json
{"GroupsModel": {
    "properties": {
        "id": {
            "default": null,
            "description": "Id of new group",
            "name": "id",
            "required": false,
            "type": "integer"
            },
        "name": {
            "default": null,
            "description": null,
            "name": "name",
            "required": true,
            "type": "string"
        }
    },
    "type": "object"
}
```

## Using authentication

In the example above, the view `UserItemResource` is a subclass of `Resource`, which is provided by `flask_restful`. However,
`flask_restful_swagger_3` provides a thin wrapper around `Resource` to provide authentication. By using this, you can
not only prevent access to resources, but also hide the documentation depending on the provided `api_key`.

Example:

```python
# Import Api and Resource instead from flask_restful_swagger_2
from flask_restful_swagger_3 import Api, swagger, Resource

api = Api(app)
def auth(api_key, endpoint, method):
    # Space for your fancy authentication. Return True if access is granted, otherwise False
    # api_key is extracted from the url parameters (?api_key=foo)
    # endpoint is the full swagger url (e.g. /some/{value}/endpoint)
    # method is the HTTP method
    return True

swagger.auth = auth

class MyView(Resource):
    @swagger.tags(...)
    # documentation..
    def get(self):
        return SomeModel(value=5)

api.add_resource(MyView, '/some/endpoint')
```

## Specification document

The `open_api_json` method of the Api instance returns the specification document object,
which may be useful for integration with other tools for generating formatted output or client code.

## Using Flask Blueprints

To use Flask Blueprints, create a function in your views module that creates the blueprint,
registers the resources and returns it wrapped in an Api instance:

```python
from flask import Blueprint, request
from flask_restful_swagger_3 import Api, swagger, Resource

class UserResource(Resource):
...

class UserItemResource(Resource):
...

def get_user_resources():
    """
    Returns user resources.
    :param app: The Flask instance
    :return: User resources
    """
    blueprint = Blueprint('user', __name__)

    api = Api(blueprint)

    api.add_resource(UserResource, '/api/users')
    api.add_resource(UserItemResource, '/api/users/<int:user_id>')

    return api
```

In your initialization module, collect the swagger document objects for each
set of resources, then use the `get_swagger_blueprint` function to combine the
documents and specify the URL to serve them at (default is '/api/doc').
Note that the `get_swagger_blueprint` function accepts the same keyword parameters
as the `Api` class to populate the fields of the combined swagger document.
Finally, register the swagger blueprint along with the blueprints for your
resources.

```python
from flask_restful_swagger_3 import get_swagger_blueprint

...

# A list of swagger document objects
docs = []

# Get user resources
user_resources = get_user_resources()

SWAGGER_URL = '/api/doc'  # URL for exposing Swagger UI (without trailing '/')
API_URL = 'swagger.json'  # Our API url (can of course be a local resource)

swagger_blueprint = get_swagger_blueprint(
    user_resources.open_api_json,
    swagger_prefix_url=SWAGGER_URL,
    swagger_url=API_URL,
    title='Example', version='1', servers=servers)


app.register_blueprint(swagger_blueprint)
```


If you want to add a url_prefix to your swagger Blueprint, you must add `SWAGGER_BLUEPRINT_URL_PREFIX` to the config of flask object and call `get_swagger_blueprint` in `app_context`

```python
from flask_restful_swagger_3 import get_swagger_blueprint

...

app.config.setdefault('SWAGGER_BLUEPRINT_URL_PREFIX', '/swagger')

with app.app_context():
    swagger_blueprint = get_swagger_blueprint(
        user_resources.open_api_json,
        swagger_prefix_url=SWAGGER_URL,
        swagger_url=API_URL,
        title='Example', version='1', servers=servers)


app.register_blueprint(swagger_blueprint, url_prefix='/swagger')
```

Refer to the files in the `example` folder for the complete code.

## Running and testing

To run the example project in the `example` folder:

```shell script
pip install flask-restful-swagger-3
python app.py
```

To run the example which uses Flask Blueprints:

```shell script
python app_blueprint.py
```

The swagger spec will by default be at `http://localhost:5000/api/doc/swagger.json`. You can change the URL by passing
`SWAGGER_URL='/my/path'` and `API_URL='myurl' to the `Api` constructor.

You can explore your api by running : [http://localhost:5000/api/doc](http://localhost:5001/api/doc)

To run tests:

```shell script
pip install tox # needed to run pytest
tox
```
