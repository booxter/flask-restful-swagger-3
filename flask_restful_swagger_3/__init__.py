import os
import json
import inspect
from copy import deepcopy

from flask import Blueprint, request, render_template, send_from_directory, current_app
from flask_restful import (Api as restful_Api, abort as flask_abort,
                           Resource as flask_Resource)

from flask_restful_swagger_3.exceptions import SchemaAlreadyExist
from flask_restful_swagger_3.swagger import (ValidationError, create_open_api_resource,
                                             add_parameters, validate_path_item_object,
                                             validate_components_object, validate_open_api_object,
                                             extract_swagger_path, _auth as auth,
                                             slash_join, REGISTRY_SCHEMA)

from flask_restful_swagger_3.constants import TypeSwagger

from flask_restful_swagger_3.swagger_format import get_validate_format


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
        add_api_spec_resource = kwargs.pop("add_api_spec_resource", True)
        authorizations = kwargs.pop("authorizations", None)

        if authorizations:
            self.open_api_object["components"]["securitySchemes"] = authorizations

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
        # examples = {}
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
                custom_example_list = f.__dict__.get("__custom_example", [])
                summary_list = f.__dict__.get("__summary", [])

                assert (
                    len(response_code_list) == len(description_list) == len(model_list) ==
                    len(no_content_list) == len(custom_example_list) == len(summary_list)
                )

                if reqparser:
                    parser_json_result, _params = RequestParserExtractor(reqparser).extract()
                    if parser_json_result and request_body:
                        raise ValidationError("requestBody and reqparser can't be in same spec")
                    request_body = parser_json_result
                    params += _params

                result_model = [self.__build_model(model) for model in model_list]

                for param in params:
                    if "schema" in param:
                        if type(param["schema"]) is type and param["schema"].__name__ in REGISTRY_SCHEMA:
                            result_model.append(self.__build_model(param["schema"]))

                for result in result_model:
                    if result:
                        schemas.update(result["reusable_schema"])

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
                        result_model[index]["example"]
                        if result_model[index]
                        else None
                    )
                    response = self.__build_responses(
                        response_code,
                        ref=ref or req_ref,
                        custom_example=custom_example_list[index],
                        example=example_schema or req_example,
                        description=description_list[index],
                        no_content=no_content_list[index]
                    )

                    for url in args:
                        if url.endswith('/'):
                            raise ValidationError('paths must not have ending slash')
                        if self.blueprint and self.blueprint.url_prefix:
                            if not self.blueprint.url_prefix.startswith('/'):
                                raise ValidationError('url_prefix must start with a leading slash')
                            if self.blueprint.url_prefix.endswith('/'):
                                raise ValidationError('url_prefix must not have ending slash')
                            url = self.blueprint.url_prefix + url

                        converted_url, parameters = self.__build_parameters(url, params)

                        __method[method]['tags'] = tags
                        __method[method].update(parameters)

                        if "responses" in __method[method]:
                            __method[method]["responses"].update(response)
                        else:
                            __method[method]["responses"] = response

                        if "summary" not in __method[method]:
                            if summary_list[index]:
                                __method[method]["summary"] = summary_list[index]

                            elif len(tags) > 0:
                                __method[method]["summary"] = f"Operations on {', '.join(tags).lower()}"

                        validate_path_item_object(__method)

                        if converted_url in urls:
                            urls[converted_url].update(__method)
                        else:
                            urls[converted_url] = __method

        self.__open_api_object["paths"].update(urls)

        if "schemas" in self.__open_api_object["components"]:
            self.__open_api_object["components"]["schemas"].update(schemas)
        else:
            self.__open_api_object["components"]["schemas"] = schemas

        if 'externalDocs' in self.__open_api_object and not self.__open_api_object['externalDocs']:
            del self.__open_api_object['externalDocs']

        validate_open_api_object(self.open_api_object)

        super().add_resource(resource, *args, endpoint=endpoint, **kwargs)

    @staticmethod
    def __swagger_url(url_prefix: str, url: str):
        new_url = slash_join(url_prefix, url)

        return new_url

    @staticmethod
    def __build_model(schema):
        if schema:
            is_list = type(schema) == list
            try:
                schema_name = schema[0].__name__ if is_list else schema.__name__
                if schema_name not in REGISTRY_SCHEMA:
                    raise TypeError("'schema' used with 'reorder_with' must be a sub class of Schema")
            except AttributeError:
                raise TypeError("'schema' used with 'reorder_with' must be a sub class of Schema")

            definition = schema[0].definitions() if is_list else schema.definitions()
            reference = schema[0].reference() if is_list else schema.reference()
            _schema = json.loads(json.dumps(definition, cls=DefinitionEncoder))

            example = (
                [json.loads(json.dumps(schema[0].example(), cls=ExampleEncoder))]
                if is_list
                else json.loads(json.dumps(schema.example(), cls=ExampleEncoder))
            )

            schema_example_name = schema[0].reference_example_name() if is_list else schema.reference_example_name()
            reference_example = schema[0].reference_example() if is_list else schema.reference_example()

            return {
                "reusable_schema": {schema_name: _schema},
                "reference": reference,
                "reference_example": {schema_example_name: reference_example},
                "reusable_example": {schema_example_name: {'value': example}},
                "example": example
            }

    @staticmethod
    def __build_responses(response_code, description="", ref=None,
                          custom_example=None, example=None, no_content=False):
        responses = {response_code: {"content": {"application/json": {}}}}

        if description:
            responses[response_code]["description"] = description

        if ref:
            _schema = {"schema": ref}
            responses[response_code]["content"]["application/json"].update(_schema)

        if custom_example:
            custom_example = {"example": custom_example}
            responses[response_code]["content"]["application/json"].update(custom_example)

        if example:
            _example = {"example": example}
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
                    f"You must define one converter for a variable_name, "
                    f"if you want several converter don't mention any '{':'.join(converter_variable[:-1])}'"
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

            result["requestBody"]["content"]["application/json"].update(reference)

            return model["reusable_schema"],  result

        return None, result

    @property
    def open_api_object(self):
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
            if issubclass(type_, str):
                return 'string'
        except TypeError:
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
    if target_class.__name__ in REGISTRY_SCHEMA:
        raise SchemaAlreadyExist(target_class.__name__)
    REGISTRY_SCHEMA[target_class.__name__] = target_class


class Schema(dict):
    properties = None

    def __init_subclass__(cls, **kwargs):
        register_schema(cls)
        super().__init_subclass__(**kwargs)
        super_classes = cls.get_super_classes()
        properties = {}
        if cls.properties:
            if type(cls.properties) is not dict:
                raise TypeError(f"Attribute 'properties' must be a 'dict', but was {type(cls.properties)}")
            properties = cls.update_properties(properties, cls.properties)
        if hasattr(cls, 'required'):
            if type(cls.required) not in [list, set, tuple]:
                raise TypeError(f"Attribute 'required' must be 'list', 'set' or 'tuple', but was {type(cls.required)}")
        for super_class in super_classes:
            if super_class.type != 'object':
                raise TypeError("You can inherit only schema of type 'object'")
            if cls.type != super_class.type:
                raise TypeError(f"You can't add type to '{cls.__name__}' " +
                                f"because it inherits of type of '{super_class.__name__}'")

            cls.type = super_class.type

            if super_class.properties:
                properties = cls.update_properties(super_class.properties, properties)

            if hasattr(super_class, 'required'):
                if hasattr(cls, 'required'):
                    cls.required = list(set(cls.required + super_class.required))

        if properties:
            cls.properties = properties

        cls.check_schema_type()

        if cls.properties and not hasattr(cls, 'type'):
            cls.type = 'object'

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
                    self.prop = self.properties[k].definitions()
                else:
                    self.prop = self.properties[k]

                nullable = self.get_boolean_attribute('nullable')
                load_only = self.get_boolean_attribute('load_only')
                dump_only = self.get_boolean_attribute('dump_only')
                if load_only and dump_only:
                    raise TypeError('A value can\'t be load_only and dump_only in the same schema')

                type_ = self.prop.get('type', None)
                format_ = self.prop.get('format', None)

                if not (nullable and v is None):
                    self.check_type(type_, k, v)
                    if 'enum' in self.prop:
                        if type(self.prop['enum']) not in [set, list, tuple]:
                            raise TypeError(f"'enum' must be 'list', 'set' or 'tuple',"
                                            f"but was {type(self.prop['enum'])}")
                        for item in list(self.prop['enum']):
                            self.check_type(type_, 'enum', item)
                        if v not in self.prop['enum']:
                            raise ValueError(f"{k} must have {' or '.join(self.prop['enum'])} but have {v}")

                    self.check_format(type_, format_, v)

                if load_only:
                    del self[k]
                    continue

                self[k] = v

        if hasattr(self, 'required'):
            self.required = list(self.required)
            for key in self.required:
                if key not in kwargs:
                    raise ValueError('The attribute "{0}" is required'.format(key))

    def get_boolean_attribute(self, attr):
        _attr = False
        if attr in self.prop:
            if self.prop[attr] not in ['true', 'false', True, False]:
                raise ValueError(f'"{attr}" must be "true", "false", True, False')
            if self.prop[attr] == 'true' or self.prop[attr]:
                _attr = True

        return _attr

    @classmethod
    def check_schema_type(cls):
        if hasattr(cls, 'type'):
            if cls.type == 'object' and not cls.properties:
                raise TypeError("Attribute properties cannot be None when schema type is object")
            if cls.type == 'array':
                if (not type(cls.items) is dict) or (inspect.isclass(cls.items) and not issubclass(cls.items, Schema)):
                    raise TypeError(f"Attribute items must be of type dict or a subclass of Schema,"
                                    f" but was {type(cls.items)}")

    @staticmethod
    def update_properties(original, new):
        if not original:
            return new
        updated = deepcopy(original)
        try:
            new_ = new.definitions()
        except AttributeError:
            new_ = new
        for prop, dict_or_schema in new_.items():
            try:
                new_prop = new_[prop].definitions()
            except AttributeError:
                new_prop = new_[prop]
            if prop in updated:
                try:
                    _dict_or_schema = dict_or_schema.definitions()
                except AttributeError:
                    _dict_or_schema = dict_or_schema
                for k, v in _dict_or_schema.items():
                    try:
                        updated_prop = updated[prop].definitions()
                    except AttributeError:
                        updated_prop = updated[prop]
                    if k in updated_prop.keys():
                        if k == 'type' and updated_prop[k] != v:
                            raise TypeError("You can't alter type of properties in sub schema")

                try:
                    if updated[prop].type == 'object':
                        updated[prop] = updated[prop].update_properties(updated[prop].properties, new[prop].properties)
                    else:
                        updated[prop] = new_prop
                except AttributeError:
                    updated[prop].update(new_prop)
            else:
                updated[prop] = new_prop

        return updated

    @classmethod
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
                        for v in value:
                            self.check_type(cls.type,  key, v)
            if type_ == 'integer' and not isinstance(value, int):
                raise ValueError(f'The attribute "{key}" must be an int, but was "{type(value)}"')
            if type_ == 'number' and not isinstance(value, int) and not isinstance(value, float):
                raise ValueError(
                    f'The attribute "{key}" must be an int or float, but was "{type(value)}"')
            if type_ == 'string' and not isinstance(value, str):
                raise ValueError(f'The attribute "{key}" must be a string, but was "{type(value)}"')
            if type_ == 'boolean' and not isinstance(value, bool):
                raise ValueError(f'The attribute "{key}" must be a bool, but was "{type(value)}"')

    @staticmethod
    def check_format(type_, format_, value):
        validator = get_validate_format(type_, format_)
        if validator:
            validator().validate(value)

    @classmethod
    def reference(cls):
        return {'$ref': f'#/components/schemas/{cls.__name__}'}

    @classmethod
    def reference_example_name(cls):
        return f'Example{cls.__name__}'

    @classmethod
    def reference_example(cls):
        return {'$ref': f'#/components/examples/{cls.reference_example_name()}'}

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
        if "type" in items:
            if items["type"] == "object":
                return cls.__example_object(items)
            else:
                return cls.__example(items)

    @staticmethod
    def __example_object(items):
        properties = items["properties"]
        example = {}
        for k, v in properties.items():
            try:
                load_only = 'load_only' in v and v['load_only']
            except TypeError:
                load_only = hasattr(v, 'load_only') and v.load_only
            try:
                if load_only:
                    continue
                val = v["type"]
                if v["type"] == "array":
                    if "items" in v:
                        try:
                            val = [v["items"].example()]
                        except AttributeError:
                            val = [v["items"]["type"]]

            except TypeError:
                val = [] if v == "array" else v
            example.update({k: val})
        return example

    @staticmethod
    def __example(items):
        if items["type"] == 'array':
            try:
                return [items.example()]
            except AttributeError:
                return [items['items']["type"]]
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

    authorizations = kwargs.pop("authorizations", None)

    if authorizations:
        if "securitySchemes" in swagger_object["components"]:
            swagger_object["components"]["securitySchemes"].update(authorizations)
        else:
            swagger_object["components"]["securitySchemes"] = authorizations

    add_parameters(swagger_object, kwargs)
    validate_open_api_object(swagger_object)

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
