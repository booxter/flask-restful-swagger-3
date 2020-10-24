import os
import json
from copy import deepcopy

from flask import Blueprint, request, render_template, send_from_directory, current_app
from flask_restful import (Api as restful_Api, abort as flask_abort,
                           Resource as flask_Resource)

from flask_restful_swagger_3.swagger import (ValidationError, create_open_api_resource,
                                             add_parameters, validate_path_item_object,
                                             validate_operation_object,
                                             validate_components_object,
                                             extract_swagger_path, _auth as auth,
                                             slash_join, TypeSwagger, REGISTRY_SCHEMA)


def abort(http_status_code, schema=None, **kwargs):
    if schema:
        kwargs.update(schema)
    flask_abort(http_status_code, **kwargs)


class ModelError(Exception):
    pass


def auth_required(f):
    """Decorator which checks if the request is permitted to call the view"""

    def decorator(*args, **kwargs):
        if not auth(request.args.get('api_key'), extract_swagger_path(request.url_rule.rule), request.method):
            abort(401)
        return f(*args, **kwargs)

    return decorator


class Resource(flask_Resource):
    decorators = [auth_required]


class Api(restful_Api):
    def __init__(self, *args, **kwargs):
        self.__open_api_object = {
            "openapi": "3.0.2",
            "info": {
                "description": "",
                "termsOfService": "",
                "title": "Example",
                "contact": {},
                "license": {},
                "version": "1",
            },
            "servers": [],  # servers replace host, basePath and schemes
            "components": {},
            "paths": {},
            "security": [],
            "tags": [],
            "externalDocs": {},
        }

        swagger_prefix_url = kwargs.pop("swagger_prefix_url", "/api/doc")
        swagger_url = kwargs.pop("swagger_url", "swagger.json")
        add_api_spec_resource = kwargs.pop('add_api_spec_resource', True)

        add_parameters(self.__open_api_object, kwargs)

        super().__init__(*args, **kwargs)

        open_api_url = self.__swagger_url(
            url_prefix=swagger_prefix_url,
            url=swagger_url,
        )

        if add_api_spec_resource:
            self.add_resource(
                create_open_api_resource(self.__open_api_object),
                open_api_url,
                endpoint="open_api",
            )

    def add_resource(self, resource, *args, endpoint=None, **kwargs):
        schemas = {}
        urls = {}

        for method in [m.lower() for m in resource.methods]:
            __method = {method: {}}
            f = resource.__dict__.get(method, None)
            if f:
                response_code_list = f.__dict__.get("__response_code", [])
                description_list = f.__dict__.get("__description", [])
                model_list = f.__dict__.get("__schema", [])
                request_body = f.__dict__.get("__request_body", None)
                params = f.__dict__.get("__params", [])
                reqparser = f.__dict__.get("__reqparser", [])
                tags = f.__dict__.get("__tags", [])
                no_content_list = f.__dict__.get("__no_content", [])

                assert (
                    len(response_code_list) == len(description_list) == len(model_list) == len(no_content_list)
                )

                if reqparser and request_body:
                    raise ValidationError("requestBody and reqparser can't be in same spec")

                if reqparser:
                    request_body, _params = RequestParserExtractor(reqparser).extract()
                    params += _params

                result_model = [self.__build_model(model) for model in model_list]

                for param in params:
                    if "schema" in param:
                        if type(param["schema"]) is type and param["schema"].__name__ in REGISTRY_SCHEMA:
                            result_model.append(self.__build_model(param["schema"]))

                for result in result_model:
                    if result:
                        schemas.update(result["schema"])

                req_ref = None
                req_example = None
                if request_body:
                    req_schema, req_body = self.__build_request_body(request_body)
                    __method[method].update(req_body)
                    if req_schema:
                        schemas.update(req_schema)

                    req_result_model = self.__build_model(request_body['schema'] if request_body else None)
                    req_ref = (
                            req_result_model["reference"]
                            if req_result_model
                            else None
                        )
                    req_example = (
                        req_result_model["example"]
                        if req_result_model
                        else None
                    )

                for index, response_code in enumerate(response_code_list):
                    ref = (
                        result_model[index]["reference"]
                        if result_model[index]
                        else None
                    )
                    example_schema = (
                        result_model[index]["example"] if result_model[index] else None
                    )
                    response = self.__build_responses(
                        response_code,
                        ref=ref or req_ref,
                        example_schema=example_schema or req_example,
                        description=description_list[index],
                        no_content=no_content_list[index]
                    )

                    for url in args:
                        if not url.startswith('/'):
                            raise ValidationError('paths must start with a /')
                        if self.blueprint and self.blueprint.url_prefix:
                            if not self.blueprint.url_prefix.startswith('/'):
                                raise ValidationError('url_prefix must start with a /')
                            if self.blueprint.url_prefix.endswith('/'):
                                raise ValidationError('url_prefix must not end with a /')
                            url = self.blueprint.url_prefix + url

                        converted_url, parameters = self.__build_parameters(url, params)

                        __method[method]['tags'] = tags
                        __method[method].update(parameters)

                        if "responses" in __method[method]:
                            __method[method]["responses"].update(response)
                        else:
                            __method[method]["responses"] = response

                        validate_path_item_object(__method)

                        if converted_url in urls:
                            urls[converted_url].update(__method)
                        else:
                            urls[converted_url] = __method

        self.__open_api_object["paths"].update(urls)

        validate_components_object(schemas)

        if "schemas" in self.__open_api_object["components"]:
            self.__open_api_object["components"]["schemas"].update(schemas)
        else:
            self.__open_api_object["components"]["schemas"] = schemas

        super().add_resource(resource, *args, endpoint=endpoint, **kwargs)

    @staticmethod
    def __swagger_url(url_prefix: str, url: str):
        new_url = slash_join(url_prefix, url)

        return new_url

    @staticmethod
    def __build_model(schema):
        if schema:
            is_list = type(schema) == list
            schema_name = schema[0].__name__ if is_list else schema.__name__

            definition = schema[0].definitions() if is_list else schema.definitions()
            reference = schema[0].reference() if is_list else schema.reference()
            _schema = eval(json.dumps(definition, cls=DefinitionEncoder))

            example = (
                [eval(json.dumps(schema[0].example(), cls=ExampleEncoder))]
                if is_list
                else eval(json.dumps(schema.example(), cls=ExampleEncoder))
            )

            return {
                "schema": {schema_name: _schema},
                "reference": reference,
                "example": example,
            }

    @staticmethod
    def __build_responses(response_code, description="", ref=None, example_schema=None, no_content=False):
        responses = {response_code: {"content": {"application/json": {}}}}

        if description:
            responses[response_code]["description"] = description

        if ref:
            _schema = {"schema": ref}
            responses[response_code]["content"]["application/json"].update(_schema)

        if example_schema:
            _example = {"example": example_schema}
            responses[response_code]["content"]["application/json"].update(_example)

        if no_content:
            del responses[response_code]["content"]

        return responses

    @staticmethod
    def __build_parameters(url, additional_parameters=[]):
        new_url, _parameters = extract_swagger_path(url)
        parameters = []
        for param in _parameters:
            converter_variable = param.split(":")
            if len(converter_variable) > 2:
                raise ValueError(
                    f"You must define one converter for a variable_name, if you want several converter don't mention any '{param}'"
                )

            try:
                converter, variable_name = converter_variable
            except ValueError:
                converter, variable_name = None, converter_variable[0]

            parameter = {
                "description": variable_name,
                "in": "path",
                "name": variable_name,
                "required": "true",
            }

            _type = TypeSwagger.get_type(converter)
            if _type:
                parameter["schema"] = {"type": _type}

            parameters.append(parameter)

        if additional_parameters:
            for param in additional_parameters:
                try:
                    param["schema"] = param["schema"].reference()
                except AttributeError:
                    if not type(param["schema"]) == dict:
                        raise ValidationError(f"'schema' must be of type 'dict' or subclass of 'Schema', not {type(param['schema'])}")

                parameters.append(param)

        return new_url, {"parameters": parameters}

    def __build_request_body(self, request_body):
        schema = None
        required = False

        if request_body and request_body["schema"]:
            schema = request_body["schema"]

        if request_body and request_body["required"]:
            required = request_body["required"]

        result = {
            "requestBody": {
                "content": {"application/json": {}},
                "description": "Request body",
                "required": required,
            }
        }

        if schema:
            model = self.__build_model(schema)
            reference = {"schema": model["reference"]}

            result["requestBody"]["content"]["application/json"] = reference

            return model["schema"], result

        return None, result

    @property
    def blueprint_name(self):
        return repr(super().__class__)

    @property
    def open_api_json(self):
        return self.__open_api_object


class RequestParserExtractor:
    """
    Uses for extraction of swagger.doc objects, which contains 'reqparser' parameter
    """

    def __init__(self, reqparser):
        self._reqparser = reqparser

    def extract(self):
        return self._extract_with_reqparser(self._reqparser)

    def _extract_with_reqparser(self, reqparser):
        if not reqparser:
            return []
        if "name" not in reqparser:
            raise ValidationError("name must be define in reqparser")
        if "parser" not in reqparser:
            raise ValidationError("parser must be define in reqparser")
        return self._get_reqparse_args(reqparser)
        # return self._extract_schemas(operation)

    def _get_reqparse_args(self, reqparser):
        """
        Get arguments from specified RequestParser and converts it to swagger representation
        """
        model_data = {'model_name': reqparser['name'], 'properties': [], 'required': []}
        make_model = False
        params = []
        request_body = {}
        for arg in reqparser['parser'].args:
            if 'json' in arg.location:
                make_model = True
                if arg.required:
                    model_data['required'].append(arg.name)
                model_data['properties'].append(self._reqparser_arg_to_swagger_param(arg))
            else:
                param = self._reqparser_arg_to_swagger_param(arg)
                # note: "cookies" location not supported by swagger
                if arg.location == 'args':
                    param['in'] = 'query'
                elif arg.location == 'headers':
                    param['in'] = 'header'
                elif arg.location == 'view_args':
                    param['in'] = 'path'
                else:
                    param['in'] = arg.location
                params.append(param)

        if make_model:
            model = self.__make_model(**model_data)
            request_body = {'schema': model, 'required': model.is_required()}
        return request_body, params

    @staticmethod
    def _get_swagger_arg_type(type_):
        """
        Converts python-type to swagger type
        If type don't supports, tries to get `swagger_type` property from `type_`
        :param type_:
        :return:
        """
        if hasattr(type_, 'swagger_type'):
            return type_.swagger_type
        elif callable(type_) and type_.__name__ == 'boolean':  # flask-restful boolean
            return 'boolean'
        elif issubclass(type_, str):
            return 'string'
        elif type_ == float:
            return 'float'
        elif type_ == int:
            return 'integer'
        elif type_ == bool:
            return 'boolean'
        elif type_ == bin:
            return 'binary'
        elif type_ == list:
            return 'array'
        elif type_ == dict:
            return 'object'
        try:
            if type_ == long:
                return 'long'
        except NameError:
            pass
        raise TypeError('unexpected type: {0}'.format(type_))

    @classmethod
    def _reqparser_arg_to_swagger_param(cls, arg):
        """
        Converts particular RequestParser argument to swagger repr
        :param arg:
        :return:
        """
        param = {'name': arg.name,
                 'description': arg.help,
                 'required': arg.required}
        if arg.choices:
            param['enum'] = arg.choices
        if arg.default:
            param['default'] = arg.default
            if callable(param['default']):
                param['default'] = getattr(param['default'], 'swagger_default', None)
        if arg.action == 'append':
            cls.__update_reqparser_arg_as_array(arg, param)
        else:
            param['type'] = cls._get_swagger_arg_type(arg.type)
        return param

    @staticmethod
    def __make_model(**kwargs):
        """
        Creates new `Schema` type, which allows if location of some argument == 'json'
        """

        required = kwargs.pop('required')
        properties = {}
        for i in range(len(kwargs['properties'])):
            name = kwargs['properties'][i].pop('name')
            del kwargs['properties'][i]['required']
            properties[name] = {k: v for k, v in kwargs['properties'][i].items() if v}

        new_model = type(
            kwargs['model_name'],
            (Schema,),
            {'type': 'object', 'properties': properties, 'required': required}
        )

        return new_model

    @classmethod
    def __update_reqparser_arg_as_array(cls, arg, param):
        param['items'] = {'type': cls._get_swagger_arg_type(arg.type)}
        param['type'] = 'array'


def register_schema(target_class):
    REGISTRY_SCHEMA[target_class.__name__] = target_class


class Schema(dict):
    properties = None

    def __init_subclass__(cls, **kwargs):
        if cls not in REGISTRY_SCHEMA:
            register_schema(cls)
        super().__init_subclass__(**kwargs)
        super_classes = cls.get_super_classes(cls)
        properties = {}
        if cls.properties:
            properties.update(deepcopy(cls.properties))
        for super_class in super_classes:
            if not hasattr(super_class, 'type'):
                raise TypeError("You can inherit only schema of type 'object'")
            if super_class.type != 'object':
                raise TypeError("You can inherit only schema of type 'object'")
            if cls.type != super_class.type:
                raise TypeError(f"You can't add type to '{cls.__name__}'" +
                                f"because it inherits of type of '{super_class.__name__}'")

            cls.type = super_class.type

            if super_class.properties:
                properties.update(deepcopy(super_class.properties))

            if hasattr(super_class, 'required'):
                if hasattr(cls, 'required'):
                    cls.required = list(set(cls.required + super_class.required))
                else:
                    cls.required = super_class.required

        if properties:
            cls.properties = properties

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.properties:
            for k, v in kwargs.items():
                if k not in self.properties:
                    raise ValueError(
                            'The model "{0}" does not have an attribute "{1}"'.format(self.__class__.__name__, k))
                if type(self.properties[k]) == type:
                    if self.properties[k].type == 'object':
                        self.properties[k](**v)
                    prop = self.properties[k].definitions()
                else:
                    prop = self.properties[k]

                nullable = False
                if 'nullable' in prop:
                    if prop['nullable'] not in ['true', 'false']:
                        raise ValueError('\'nullable\' must be \'true\' or \'false\'')
                    if prop['nullable'] == 'true':
                        nullable = True

                if nullable and v is None:
                    continue

                type_ = None
                if 'type' in prop:
                    type_ = prop['type']
                self.check_type(type_, k, v)

                if 'enum' in prop:
                    if type(prop['enum']) not in [set, list, tuple]:
                        raise TypeError(f"'enum' is must be 'list', 'set' or 'tuple', but was {type(prop['enum'])}")
                    for item in list(prop['enum']):
                        self.check_enum_type(type_, item)
                    if v not in prop['enum']:
                        raise ValueError(f"{k} must have {' or '.join(prop['enum'])} but have {v}")
                self[k] = v

        if hasattr(self, 'required'):
            for key in self.required:
                if key not in kwargs:
                    raise ValueError('The attribute "{0}" is required'.format(key))

    @staticmethod
    def get_super_classes(cls):
        return [
            schema for schema_name, schema in REGISTRY_SCHEMA.items()
            if schema_name != cls.__name__ and issubclass(cls, schema)
        ]

    def check_type(self, type_, key, value):
        if type_:
            if type_ == 'array':
                if not isinstance(value, list):
                    raise ValueError(f'The attribute "{key}" must be a list, but was "{type(value)}')
                cls = self.properties[key].get('items')
                if cls and cls.__name__ in REGISTRY_SCHEMA:
                    if cls.type == 'object':
                        for v in value:
                            cls(**v)
                    else:
                        self.check_array_type(cls.type, key, value)
            if type_ == 'integer' and not isinstance(value, int):
                raise ValueError(f'The attribute "{key}" must be an int, but was "{type(value)}"')
            if type_ == 'number' and not isinstance(value, int) and not isinstance(value, float):
                raise ValueError(
                    f'The attribute "{key}" must be an int or float, but was "{type(value)}"')
            if type_ == 'string' and not isinstance(value, str):
                raise ValueError(f'The attribute "{key}" must be a string, but was "{type(value)}"')
            if type_ == 'boolean' and not isinstance(value, bool):
                raise ValueError(f'The attribute "{key}" must be an int, but was "{type(value)}"')

    @staticmethod
    def check_array_type(type_, key, value):
        if type_:
            if type_ == 'integer' and not all([isinstance(v, int) for v in value]):
                raise ValueError(f'The list "{key}" must have all items of type int')
            if type_ == 'number' and not all([isinstance(v, int) for v in value]) and not all([isinstance(v, float) for v in value]):
                raise ValueError(
                    f'The list "{key}" must have all items of type int or float')
            if type_ == 'string' and not all([isinstance(v, str) for v in value]):
                raise ValueError(f'The list "{key}" must have all items of type string')
            if type_ == 'boolean' and not all([isinstance(v, bool) for v in value]):
                raise ValueError(f'The list "{key}" must have all items of type string')

    @staticmethod
    def check_enum_type(type_, value):
        if type_:
            if type_ == 'integer' and not isinstance(value, int):
                raise ValueError(f'The enum "{value}" must be an int, but was "{type(value)}"')
            if type_ == 'number' and not isinstance(value, int) and not isinstance(value, float):
                raise ValueError(
                    f'The enum "{value}" must be an int or float, but was "{type(value)}"')
            if type_ == 'string' and not isinstance(value, str):
                raise ValueError(f'The enum "{value}" must be a string, but was "{type(value)}"')
            if type_ == 'boolean' and not isinstance(value, bool):
                raise ValueError(f'The enum "{value}" must be an int, but was "{type(value)}"')

    @classmethod
    def reference(cls):
        return {'$ref': '#/components/schemas/{0}'.format(cls.__name__)}

    @classmethod
    def definitions(cls):
        return {k: v for k, v in cls.__dict__.items() if not k.startswith('_')}

    @classmethod
    def array(cls):
        return {'type': 'array', 'items': cls}

    @classmethod
    def is_required(cls):
        return bool(filter(lambda x: bool(x), map(lambda x: x['required'], cls.properties.values())))

    @classmethod
    def example(cls):
        items = dict(cls.__dict__.items())
        if "properties" in items:
            properties = dict(cls.__dict__.items())["properties"]
            example = {}
            if properties:
                for k, v in properties.items():
                    if type(v) is dict:
                        val = v["type"]
                        if v["type"] == "array":
                            if "items" in v:
                                val = [v["items"].example()]
                            else:
                                val = []
                    else:
                        val = [] if v == "array" else v
                    example.update({k: val})
            return example
        return items["type"]


class DefinitionEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.definitions()


class ExampleEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.example()


def get_swagger_blueprint(
        swagger_object,
        swagger_prefix_url="/api/doc",
        swagger_url="/swagger.json",
        config=None,
        oauth_config=None,
        **kwargs):
    """
    Returns a Flask blueprint to serve the given list of swagger document objects.
    :param swagger_object: The swagger objects
    :param swagger_prefix_url: The URL prefix path that serves the swagger specification document
    :param swagger_url: The URL that serves the swagger specification document
    :param config: Additional config
    :param oauth_config
    :return: A Flask blueprint
    """

    add_parameters(swagger_object, kwargs)
    app_name = kwargs.get('title', 'Swagger UI')
    swagger_blueprint_name = kwargs.get('swagger_blueprint_name', 'swagger')

    blueprint = Blueprint(swagger_blueprint_name, __name__, static_folder='static', template_folder='templates')

    api = restful_Api(blueprint)

    new_url = slash_join(swagger_prefix_url, swagger_url)

    try:
        blueprint_url_prefix = current_app.config.get(
            "SWAGGER_BLUEPRINT_URL_PREFIX", ""
        )
    except RuntimeError:
        blueprint_url_prefix = ""

    new_url_with_prefix = slash_join(blueprint_url_prefix, new_url)

    default_config = {
        'app_name': app_name,
        'dom_id': '#swagger-ui',
        'url': new_url_with_prefix,
        'layout': 'StandaloneLayout',
        'deepLinking': True
    }

    if config:
        default_config.update(config)

    fields = {
        # Some fields are used directly in template
        'base_url': blueprint_url_prefix,
        'app_name': default_config.pop('app_name'),
        # Rest are just serialized into json string for inclusion in the .js file
        'config_json': json.dumps(default_config),

    }
    if oauth_config:
        fields['oauth_config_json'] = json.dumps(oauth_config)

    api.add_resource(create_open_api_resource(swagger_object),
                     new_url)

    @blueprint.route('/', strict_slashes=False)
    @blueprint.route('/<path:path>', strict_slashes=False)
    def show(path=None):
        if not path or path == 'index.html':
            if not default_config.get('oauth2RedirectUrl', None):
                default_config.update(
                    {"oauth2RedirectUrl": os.path.join(request.base_url, "oauth2-redirect.html")}
                )
                fields['config_json'] = json.dumps(default_config)
            return render_template('index.template.html', **fields)
        else:
            return send_from_directory(
                # A bit of a hack to not pollute the default /static path with our files.
                os.path.join(
                    blueprint.root_path,
                    blueprint._static_folder
                ),
                path
            )

    return blueprint


def swagger_type(type_):
    """Decorator to add __swagger_type property to flask-restful custom input
    type functions
    """

    def inner(f):
        f.__swagger_type = type_
        return f

    return inner
