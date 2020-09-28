import json

from flask import Blueprint, request
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

                assert (
                    len(response_code_list) == len(description_list) == len(model_list)
                )

                # if reqparser and params:
                #     raise ValidationError("parameters and reqparser can't be in same spec")

                if reqparser and request_body:
                    print(reqparser)
                    raise ValidationError("requestBody and reqparser can't be in same spec")

                if reqparser:
                    request_body, _params = RequestParserExtractor(reqparser).extract()
                    params += _params
                    # if _params:
                    #     params += _params

                result_model = [self.__build_model(model) for model in model_list]

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

        if new_url.endswith("/"):
            return f"{new_url}swagger.json"
        if not new_url.endswith("swagger.json"):
            return f"{new_url}/swagger.json"
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
    def __build_responses(response_code, description="", ref=None, example_schema=None):
        responses = {response_code: {"content": {"application/json": {}}}}

        if description:
            responses[response_code]["description"] = description

        if ref:
            _schema = {"schema": ref}
            responses[response_code]["content"]["application/json"].update(_schema)

        if example_schema:
            _example = {"example": example_schema}
            responses[response_code]["content"]["application/json"].update(_example)

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.properties:
            for k, v in kwargs.items():
                if k not in self.properties:
                    raise ValueError(
                            'The model "{0}" does not have an attribute "{1}"'.format(self.__class__.__name__, k))
                if type(self.properties[k]) == type:
                    prop = self.properties[k].definitions()
                else:
                    prop = self.properties[k]
                if 'type' in prop:
                    type_ = prop['type']
                    if type_ == 'integer' and not isinstance(v, int):
                        raise ValueError('The attribute "{0}" must be an int, but was "{1}"'.format(k, type(v)))
                    if type_ == 'number' and not isinstance(v, int) and not isinstance(v, float):
                        raise ValueError(
                                'The attribute "{0}" must be an int or float, but was "{1}"'.format(k, type(v)))
                    if type_ == 'string' and not isinstance(v, str):
                        raise ValueError('The attribute "{0}" must be a string, but was "{1}"'.format(k, type(v)))
                    if type_ == 'boolean' and not isinstance(v, bool):
                        raise ValueError('The attribute "{0}" must be an int, but was "{1}"'.format(k, type(v)))
                self[k] = v

        if hasattr(self, 'required'):
            for key in self.required:
                if key not in kwargs:
                    raise ValueError('The attribute "{0}" is required'.format(key))

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
                        example.update({k: v["type"]})
                    else:
                        example.update({k: v})
            return example
        return items["type"]


class DefinitionEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.definitions()


class ExampleEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.example()


def get_swagger_blueprint(swagger_object, api_spec_url='/api/doc/swagger', **kwargs):
    """
    Returns a Flask blueprint to serve the given list of swagger document objects.
    :param swagger_object: The swagger objects
    :param api_spec_url: The URL path that serves the swagger specification document
    :return: A Flask blueprint
    """

    add_parameters(swagger_object, kwargs)

    blueprint = Blueprint('swagger', __name__)

    api = restful_Api(blueprint)

    api_spec_urls = [
        '{0}.json'.format(api_spec_url),
        '{0}.html'.format(api_spec_url),
    ]

    api.add_resource(create_open_api_resource(swagger_object),
                     *api_spec_urls, endpoint='swagger')

    return blueprint


def swagger_type(type_):
    """Decorator to add __swagger_type property to flask-restful custom input
    type functions
    """

    def inner(f):
        f.__swagger_type = type_
        return f

    return inner
