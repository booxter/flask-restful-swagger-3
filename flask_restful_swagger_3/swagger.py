import collections
import re
import inspect
from functools import wraps
from http import HTTPStatus

from flask import request
from flask_restful import Resource, reqparse, inputs
from flask_restful_swagger_3 import constants

REGISTRY_SCHEMA = {}

components_security_schemes = None


class ValidationError(ValueError):
    pass


def auth(api_key, endpoint, method):
    """Override this function in your application.

    If this function returns False, 401 forbidden is raised and the documentation is not visible.
    """
    return True


def _auth(*args, **kwargs):
    return auth(*args, **kwargs)


def create_open_api_resource(swagger_object):
    """Creates a flask_restful api endpoint for the swagger spec"""

    class SwaggerEndpoint(Resource):
        def get(self):
            swagger_doc = {}
            # filter keys with empty values

            for k, v in swagger_object.items():
                if v or k == 'paths':
                    if k == 'paths':
                        paths = {}
                        for endpoint, view in v.items():
                            views = {}
                            for method, docs in view.items():
                                # check permissions. If a user has not access to an api, do not show the docs of it
                                if auth(request.args.get('api_key'), endpoint, method):
                                    views[method] = docs
                            if views:
                                paths[endpoint] = views
                        swagger_doc['paths'] = collections.OrderedDict(sorted(paths.items()))
                    else:
                        swagger_doc[k] = v

                if k == 'servers':
                    validate_servers_object(v)

                if k == 'info':
                    validate_info_object(v)
                    continue

            return swagger_doc

    return SwaggerEndpoint


def set_nested(d, key_spec, value):
    """
    Sets a value in a nested dictionary.
    :param d: The dictionary to set
    :param key_spec: The key specifier in dotted notation
    :param value: The value to set
    """
    keys = key_spec.split('.')

    for key in keys[:-1]:
        d = d.setdefault(key, {})

    d[keys[-1]] = value


def add_parameters(swagger_object, parameters):
    """
    Populates a swagger document with parameters.
    :param parameters: A collection of parameters to add
    :param swagger_object: The swagger document to add parameters to
    """
    # A list of accepted parameters.  The first item in the tuple is the
    # name of keyword argument, the second item is the default value,
    # and the third item is the key name in the swagger object.
    fields = [
        ('title', '', 'info.title'),
        ('description', '', 'info.description'),
        ('terms', '', 'info.termsOfService'),
        ('version', '', 'info.version'),
        ('contact', {}, 'info.contact'),
        ('license', {}, 'info.license'),
        ('servers', [], 'servers'),
        ('components', {}, 'components'),
        ('paths', {}, 'paths'),
        ('security', [], 'security'),
        ('tags', [], 'tags'),
        ('externalDocs', {}, 'externalDocs')
    ]

    for field in fields:
        value = parameters.pop(field[0], field[1])
        if value:
            set_nested(swagger_object, field[2], value)


def get_data_type(param):
    """
    Maps swagger data types to Python types.
    :param param: swagger parameter
    :return: Python type
    """
    if not param:
        return None
    try:
        param_type = param.get('type', None)
    except TypeError:
        param_type = param.__dict__.get('type', None)
    if param_type:
        if param_type == 'array':
            if 'items' in param:
                param = param['items']
            try:
                param_type = param.get('type', None)
            except TypeError:
                param_type = param.__dict__.get('type', None)
            if param_type == 'object':
                prop = param.__dict__.get('properties', None)
                for k in prop:
                    try:
                        param_type = prop[k].get('type', None)
                    except TypeError:
                        param_type = prop[k].__dict__.get('type', None)
        if param_type == 'string':
            try:
                param_format = param.get('format', None)
            except TypeError:
                param_format = param.__dict__.get('format', None)

            if param_format == 'date':
                return inputs.date

            elif param_format == 'date-time':
                return inputs.datetime_from_iso8601

            return str

        elif param_type == 'integer':
            return int

        elif param_type == 'boolean':
            return inputs.boolean

        elif param_type == 'number':
            param_format = param.get('format', None)

            if param_format == 'float' or param_format == 'double':
                return float

    return None


def get_data_action(param):
    if param:
        try:
            param_type = param.get('type', None)
        except TypeError:
            param_type = param.__dict__.get('type', None)

        if param_type == 'array':
            return 'append'
        return 'store'

    return None


def get_parser_from_schema(param):
    ref = param['schema']['$ref']
    if type(ref) == str:
        _schema = ref.split('/')[-1]
    else:
        _schema = ref
    if _schema in REGISTRY_SCHEMA:
        definitions_schema = REGISTRY_SCHEMA[_schema]
    else:
        definitions_schema = _schema
    _type = definitions_schema.__dict__.get('type', None)
    properties = definitions_schema.__dict__.get('properties', None)
    required = definitions_schema.__dict__.get('required', [])

    _help = param.get('description', None)
    default = definitions_schema.__dict__.get('default', None)
    choices = definitions_schema.__dict__.get('enum', ())

    if _type == 'object':
        for prop in properties:
            try:
                _help = properties[prop].get('description', None)
            except TypeError:
                _help = properties[prop].__dict__.get('description', None)

            try:
                default = properties[prop].get('default', None)
            except TypeError:
                default = properties[prop].__dict__.get('default', None)

            try:
                choices = properties[prop].get('enum', ())
            except TypeError:
                choices = properties[prop].__dict__.get('enum', ())
            name = prop
            second_part = {
                'dest': prop,
                'type': get_data_type(properties[prop]),
                'location': 'args',
                'help': _help,
                'required': prop in required,
                'default': default,
                'choices': tuple(choices),
                'action': get_data_action(properties[prop])
            }
            yield name, second_part

    else:
        name = param['name']
        second_part = {
            'dest': name,
            'type': get_data_type({'type': _type}),
            'location': 'args',
            'help': _help,
            'required': param.get('required', False),
            'default': default,
            'choices': tuple(choices),
            'action': get_data_action({'type': _type})
        }
        yield name, second_part


def get_parser_arg(param):
    """
    Return an argument for the request parser.
    :param param: Swagger document parameter
    :return: Request parser argument
    """
    if 'schema' in param:
        if '$ref' in param['schema']:
            list_obj = [(name, sec) for name, sec in get_parser_from_schema(param)]
            return list_obj

    default = None
    choices = ()
    if 'schema' in param:
        if 'default' in param['schema']:
            default = param['schema']['default']
        if 'enum' in param['schema']:
            if type(param['schema']['enum']) not in [set, list, tuple]:
                raise TypeError(f"'enum' must be 'list', 'set' or 'tuple', but was {type(param['schema']['enum'])}")
            choices = tuple(param['schema']['enum'])

    obj = (
        param['name'],
        {
            'dest': param['name'],
            'type': get_data_type(param.get('schema', None)),
            'location': 'args',
            'help': param.get('description', None),
            'required': param.get('required', False),
            'default': default,
            'choices': choices,
            'action': get_data_action(param['schema'])
        })
    return obj


def get_parser_args(params):
    """
    Return a list of arguments for the request parser.
    :param params: Swagger document parameters
    :return: Request parser arguments
    """
    return [get_parser_arg(p) for p in params if p['in'] == 'query']


def get_parser(params):
    """
    Returns a parser for query parameters from swagger document parameters.
    :param params: swagger doc parameters
    :return: Query parameter parser
    """
    parser = reqparse.RequestParser()

    for arg in get_parser_args(params):
        if type(arg) == list:
            for a in arg:
                parser.add_argument(a[0], **a[1])
        else:
            parser.add_argument(arg[0], **arg[1])

    return parser


def validate_open_api_object(open_api_object):
    for k, v in open_api_object.items():
        if k not in constants.open_api_object_list:
            raise ValidationError('Invalid open api object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='https://swagger.io/specification/#OpenAPIObject'))

        if k == 'openapi':
            if type(v) is not str:
                raise ValidationError('Invalid open api object. "{0}" must be a str but was {1}'.format(k, type(v)))

        if k == 'info':
            validate_info_object(v)
            continue

        if k == 'servers':
            validate_servers_object(v)
            continue

        if k == 'paths':
            validate_paths_object(v)
            continue

        if k == 'components':
            validate_components_object(v)
            continue

        if k == 'security':
            validate_security(v)

        if k == 'tags':
            validate_tags(v)

        if k == 'externalDocs':
            validate_external_documentation_object(v)

    if 'openapi' not in open_api_object:
        raise ValidationError('Invalid open api object. Missing field "openapi"')

    if 'info' not in open_api_object:
        raise ValidationError('Invalid open api object. Missing field "info"')

    if 'paths' not in open_api_object:
        raise ValidationError('Invalid open api object. Missing field "paths"')


def validate_info_object(info_object):
    for k, v in info_object.items():
        if k not in constants.info_object_list:
            raise ValidationError('Invalid info object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='https://swagger.io/specification/#infoObject'))

        if k == 'contact':
            validate_contact_object(v)
            continue

        if k == 'license':
            validate_license_object(v)
            continue

    if 'title' not in info_object:
        raise ValidationError('Invalid info object. Missing field "title"')

    if 'version' not in info_object:
        raise ValidationError('Invalid info object. Missing field "version"')


def validate_contact_object(contact_object):
    if contact_object:
        for k, v in contact_object.items():
            if k not in constants.contact_object_list:
                raise ValidationError('Invalid contact object. Unknown field "{field}". See {url}'.format(
                    field=k,
                    url='https://swagger.io/specification/#contactObject'))

            if k == 'email':
                if not validate_email(v):
                    raise ValidationError('Invalid email. See {url}'.format(
                        url='https://swagger.io/specification/#contactObject'))


def validate_license_object(license_object):
    if license_object:
        for k, v in license_object.items():
            if k not in constants.license_object_list:
                raise ValidationError('Invalid license object. Unknown field "{field}". See {url}'.format(
                    field=k,
                    url='https://swagger.io/specification/#licenseObject'))

            if k == 'url':
                if not validate_url(v):
                    raise ValidationError('Invalid url. See {url}'.format(
                        url='https://swagger.io/specification/#licenseObject'))

        if 'name' not in license_object:
            raise ValidationError('Invalid license object. Missing field "name"')


def validate_callback_object(call_back_object):
    for k, v in call_back_object.items():
        validate_path_item_object(v)


def validate_paths_object(paths_object):
    for k, v in paths_object.items():
        if type(k) is not str:
            raise ValidationError(f'Invalid paths object. "{k}" must be a str but was "{type(v)}"')
        if not k.startswith('/'):
            raise ValidationError(f'Invalid paths object. "{k}" must start with a leading slash')
        if k.endswith('/'):
            raise ValidationError(f'Invalid paths object. "{k}" must not have an ending slash')
        validate_path_item_object(v)


def validate_path_item_object(path_item_object):
    """Checks if the passed object is valid according to https://swagger.io/specification/#pathItemObject"""
    for k, v in path_item_object.items():
        if k == '$ref':
            continue
        if k in constants.operation_object_list:
            validate_operation_object(v)
            continue
        if k == 'servers':
            validate_servers_object(v)
            continue
        if k == 'parameters':
            for parameter in v:
                try:
                    validate_reference_object(parameter)
                except ValidationError:
                    validate_parameter_object(parameter)
            continue
        if k == "summary":
            continue
        if k == "description":
            continue
        raise ValidationError('Invalid path item object. Unknown field "{field}". See {url}'.format(
            field=k,
            url='https://swagger.io/specification/#pathItemObject'))


def validate_operation_object(operation_object):
    for k, v in operation_object.items():
        if k in ['tags']:
            if isinstance(v, list):
                continue
            raise ValidationError('Invalid operation object. "{0}" must be a list but was "{1}"', k, type(v))
        if k in ['summary', 'description', 'operationId']:
            if isinstance(v, str):
                continue
            raise ValidationError('Invalid operation object. "{0}" must be a string but was "{1}"', k, type(v))
        if k in ['requestBody']:
            validate_request_body_object(v)
            continue
        if k in ['deprecated']:
            if isinstance(v, bool):
                continue
            raise ValidationError('Invalid operation object. "{0}" must be a bool but was "{1}"', k, type(v))
        if k in ['externalDocs']:
            validate_external_documentation_object(v)  # to check
            continue
        if k in ['parameters']:
            for parameter in v:
                validate_parameter_object(parameter)
            continue
        if k in ['responses']:
            validate_responses_object(v)
            continue
        if k in ['security']:
            validate_security(v)
            continue
        raise ValidationError('Invalid operation object. Unknown field "{field}". See {url}'.format(
            field=k,
            url='https://swagger.io/specification/#operationObject'))
    if 'responses' not in operation_object:
        raise ValidationError('Invalid operation object. Missing field "responses"')


def validate_map_parameter_object(map_parameter_object):
    for k, v in map_parameter_object.items():
        try:
            validate_parameter_object(v)
        except ValidationError:
            validate_reference_object(v)


def validate_parameter_object(parameter_object):
    for k, v in parameter_object.items():
        if k not in constants.parameter_object_list:
            raise ValidationError('Invalid parameter object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='https://swagger.io/specification/#parameterObject'))
    if 'name' not in parameter_object:
        raise ValidationError('Invalid parameter object. Missing field "name"')
    if 'in' not in parameter_object:
        raise ValidationError('Invalid parameter object. Missing field "in"')
    else:
        if parameter_object['in'] not in ['path', 'query', 'header', 'cookie']:
            raise ValidationError(
                'Invalid parameter object. Value of field "in" must be path, query, header, cookie was "{0}"'.format(
                    parameter_object['in']))
    if 'schema' in parameter_object:
        validate_schema_object(parameter_object['schema'])


def validate_reference_object(reference_object):
    if len(reference_object.keys()) > 1 or '$ref' not in reference_object:
        raise ValidationError('Invalid reference object. It may only contain key "$ref"')


def validate_external_documentation_object(external_documentation_object):
    for k, v in external_documentation_object.items():
        if k not in constants.external_doc_object_list:
            raise ValidationError('Invalid external documentation object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='https://swagger.io/specification/#externalDocumentationObject'))

        if k == 'description':
            if not type(v) == str:
                raise ValidationError('Invalid external documentation object.'
                                      ' "{0}" must be a str but was {1}'.format(k, type(v)))

        if k == 'url':
            validate_url(v)

    if 'url' not in external_documentation_object:
        raise ValidationError('Invalid external documentation object. Missing field "url"')


def validate_map_responses_object(map_responses_object):
    for k, v in map_responses_object.items():
        try:
            validate_reference_object(v)
        except ValidationError:
            validate_responses_object(v)


def validate_responses_object(responses_object):
    for k, v in responses_object.items():
        if type(k) not in [int, str, HTTPStatus]:
            raise ValidationError(f'Invalid responses object. '
                                  f'"{k}" must be a "int" (HttpStatusCode), a "HTTPStatus enum" or a "str" (default), '
                                  f'but was {type(k)}')
        try:
            k = int(k)
        except ValueError:
            pass

        if k not in constants.responses_object_list and k != 'default':
            raise ValidationError(f'Invalid responses object. it must be a HttpStatusCode, a HTTPStatus enum '
                                  f'or "default" but was {k}')
        try:
            validate_response_object(v)
        except ValidationError:
            validate_reference_object(v)


def validate_response_object(response_object):
    for k, v in response_object.items():
        if k == 'description':
            continue
        if k == 'headers':
            try:
                validate_reference_object(v)
                continue
            except ValidationError:
                validate_map_header_object(v)
                continue
        if k == 'content':
            validate_map_media_type_object(v)
            continue
        if k == "links":
            validate_link_object(v)
            continue
        raise ValidationError('Invalid response object. Unknown field "{field}". See {url}'.format(
            field=k,
            url='https://swagger.io/specification/#responseObject'))
    if 'description' not in response_object:
        raise ValidationError('Invalid response object. Missing field "description"')


def validate_map_request_body_object(map_request_body_object):
    for k, v in map_request_body_object.items():
        try:
            validate_request_body_object(v)
        except ValidationError:
            validate_reference_object(v)


def validate_request_body_object(request_body_object):
    for k, v in request_body_object.items():
        if k in ['description']:
            continue
        if k in ['required']:
            if isinstance(v, bool):
                continue
        if k in ['content']:
            validate_map_media_type_object(v)
            continue

    if 'content' not in request_body_object:
        raise ValidationError('Invalid request body object. Missing field "content"')


def validate_map_media_type_object(map_media_type_object):
    for k, v in map_media_type_object.items():
        if validate_media_type(k):
            validate_media_type_object(v)
            continue
        raise ValidationError(
            'Invalid content object, the field must match the following pattern ("application/json", "*/*" ...").'
            '. See https://swagger.io/specification/#mediaTypeObject'
        )


def validate_media_type_object(media_type_object):
    for k, v in media_type_object.items():
        if k == "schema":
            validate_schema_object(v)
            continue
        if k == "example":
            continue

        if k == "examples":
            validate_map_example_object(v)
            continue


def validate_security(securities):
    if type(securities) is not list:
        raise ValidationError(f'Invalid operation object. "security" must be a list but was {type(securities)}')
    for security in securities:
        validate_security_requirement_object(security)


def validate_security_requirement_object(security_requirement_object):
    global components_security_schemes
    if not components_security_schemes:
        raise ValidationError("Each property of security requirement object must correspond "
                              "to a security scheme declared in the Security Schemes under the Components Object, "
                              "but the Security Schemes is not declared. "
                              "See https://swagger.io/specification/#SecurityRequirementObject")
    for k, v in security_requirement_object.items():
        if type(v) is not list:
            components_security_schemes = None
            raise ValidationError(f'Invalid security requirement object. '
                                  f'"{k}" must be a list, but was {type(v)}')
        if k not in components_security_schemes:
            components_security_schemes = None
            raise ValidationError("Each property of security requirement object must correspond "
                                  "to a security scheme declared in the Security Schemes under the Components Object, "
                                  "See https://swagger.io/specification/#SecurityRequirementObject")
        _type = components_security_schemes[k].get('type', None)
        if _type not in ['oauth2', 'openIdConnect'] and len(v) > 0:
            components_security_schemes = None
            raise ValidationError(f'Invalid security requirement object. '
                                  f'"{k}" must be empty except for "oauth2", "openIdConnect"')

    components_security_schemes = None


def validate_map_security_scheme_object(map_security_scheme_object):
    for k, v in map_security_scheme_object.items():
        try:
            validate_security_scheme_object(v)
        except ValidationError:
            validate_reference_object(v)

    global components_security_schemes
    components_security_schemes = map_security_scheme_object


def validate_security_scheme_object(security_scheme_object):
    for k, v in security_scheme_object.items():
        if k not in constants.security_scheme_list:
            raise ValidationError('Invalid security scheme object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='https://swagger.io/specification/#SecuritySchemeObject'))

    if 'type' not in security_scheme_object:
        raise ValidationError('Invalid security scheme object. Missing field "type"')
    _type = security_scheme_object['type']
    if _type not in constants.security_scheme_object_type_list:
        raise ValidationError(f'"type" must be one of {", ".join(constants.security_scheme_object_type_list)}')
    if _type == 'apiKey':
        if 'name' not in security_scheme_object:
            raise ValidationError('Invalid security scheme object. Missing field "name" when type is "apiKey"')
        if 'in' not in security_scheme_object:
            raise ValidationError('Invalid security scheme object. Missing field "in" when type is "apiKey"')
    if _type == 'http':
        if 'scheme' not in security_scheme_object:
            raise ValidationError('Invalid security scheme object. Missing field "scheme" when type is "http"')
        scheme = security_scheme_object['scheme']
        if scheme not in constants.security_scheme_object_scheme_list:
            raise ValidationError(
                f'Invalid security scheme object. '
                f'"scheme" must be one of {", ".join(constants.security_scheme_object_scheme_list)} ')
    if _type == 'oauth2':
        if 'flows' not in security_scheme_object:
            raise ValidationError('Invalid security scheme object. Missing field "flows" when type is "oauth2"')
        validate_oauth_flows_object(security_scheme_object['flows'])
    if _type == 'openIdConnect':
        if 'openIdConnectUrl' not in security_scheme_object:
            raise ValidationError('Invalid security scheme object. Missing field '
                                  '"openIdConnectUrl" when type is openIdConnectUrl')
        if not validate_url(security_scheme_object['openIdConnectUrl']):
            raise ValidationError('Invalid url. See {url}'.format(
                url='https://swagger.io/specification/#securitySchemeObject'))


def validate_oauth_flows_object(oauth_flows_object):
    for k, v in oauth_flows_object.items():
        if k not in constants.oauth_flows_object_list:
            raise ValidationError('Invalid oauth flows object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='https://swagger.io/specification/#OAuthFlowsObject'))

    if 'implicit' in oauth_flows_object:
        _validate_oauth_flows_object('implicit', oauth_flows_object['implicit'])

    if 'password' in oauth_flows_object:
        _validate_oauth_flows_object('password', oauth_flows_object['password'])

    if 'clientCredentials' in oauth_flows_object:
        _validate_oauth_flows_object('clientCredentials', oauth_flows_object['clientCredentials'])

    if 'authorizationCode' in oauth_flows_object:
        _validate_oauth_flows_object('authorizationCode', oauth_flows_object['authorizationCode'])


def _validate_oauth_flows_object(key, oauth_flows_object):
    for k, v in oauth_flows_object.items():
        if k not in constants.oauth_flows_object_sub_level_list:
            raise ValidationError('Invalid oauth flows object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='https://swagger.io/specification/#OAuthFlowsObject'))

    if 'refreshUrl' in oauth_flows_object:
        if not validate_url(oauth_flows_object['refreshUrl']):
            raise ValidationError('Invalid url. See {url}'.format(
                url='https://swagger.io/specification/#OAuthFlowsObject'))

    if 'scopes' not in oauth_flows_object:
        raise ValidationError('Invalid oauth flows object. Missing field "scopes"')
    try:
        for k, v in oauth_flows_object['scopes'].items():
            if not type(v) is str:
                raise ValidationError('Invalid oauth flows object. "scopes" must be a dict of string')
    except AttributeError:
        raise ValidationError('Invalid oauth flows object. "scopes" must be a dict of string')
    if key == 'implicit' or key == 'authorizationCode':
        check_authorization_url(oauth_flows_object)

    if key == 'authorizationCode' or key == 'password' or key == 'clientCredentials':
        check_token_url(oauth_flows_object)


def check_authorization_url(oauth_flows_object):
    if 'authorizationUrl' not in oauth_flows_object:
        raise ValidationError('Invalid oauth flows object. Missing field "authorizationUrl"')
    if not validate_url(oauth_flows_object['authorizationUrl']):
        raise ValidationError('Invalid url. See {url}'.format(
            url='https://swagger.io/specification/#OAuthFlowsObject'))


def check_token_url(oauth_flows_object):
    if 'tokenUrl' not in oauth_flows_object:
        raise ValidationError('Invalid oauth flows object. Missing field "tokenUrl"')
    if not validate_url(oauth_flows_object['tokenUrl']):
        raise ValidationError('Invalid url. See {url}'.format(
            url='https://swagger.io/specification/#OAuthFlowsObject'))


def validate_components_object(components_object):
    for k, v in components_object.items():
        if k not in constants.components_object_list:
            raise ValidationError('Invalid components object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='https://swagger.io/specification/#ComponentsObject'))
        if k == "schemas":
            validate_map_schema_object(v)
            continue

        if k == "responses":
            validate_map_responses_object(v)
            continue

        if k == "parameters":
            validate_map_parameter_object(v)
            continue

        if k == "examples":
            validate_map_example_object(v)
            continue

        if k == "requestBodies":
            validate_map_request_body_object(v)
            continue

        if k == "headers":
            validate_map_header_object(v)
            continue

        if k == "securitySchemes":
            validate_map_security_scheme_object(v)
            continue

        if k == 'links':
            validate_map_link_object(v)
            continue

        if k == 'callbacks':
            validate_callback_object(v)


def validate_map_schema_object(map_schema_object):
    for k, v in map_schema_object.items():
        if 'properties' in v:
            continue
        validate_schema_object(v)


def validate_schema_object(schema_object):
    for k, v in schema_object.items():
        try:
            validate_reference_object(v)
        except AttributeError:
            if k == 'required' and not isinstance(v, list):
                raise ValidationError('Invalid schema object. "{0}" must be a list but was {1}'.format(k, type(v)))


def validate_map_header_object(map_header_object):
    for k, v in map_header_object.items():
        try:
            validate_header_object(v)
        except ValidationError:
            validate_reference_object(v)


def validate_header_object(header_object):
    for k, v in header_object.items():
        if k not in constants.headers_object_list:
            raise ValidationError('Invalid header object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='https://swagger.io/specification/#HeaderObject'))
        if k == 'name':
            raise ValidationError('"name" must not be specified. See https://swagger.io/specification/#HeaderObject')
        if k == 'in':
            raise ValidationError('"in" must not be specified. See https://swagger.io/specification/#HeaderObject')

        if k == 'schema':
            validate_schema_object(header_object['schema'])
            continue


def validate_map_link_object(map_link_object):
    for k, v in map_link_object.items():
        try:
            validate_link_object(v)
        except ValidationError:
            validate_reference_object(v)


def validate_link_object(link_object):
    for k, v in link_object.items():
        if k not in constants.link_object_list:
            raise ValidationError('Invalid link object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='https://swagger.io/specification/#linkObject'))

        if k == 'operationRef' and type(v) is not str:
            raise ValidationError('Invalid link object. "{0}" must be a str but was {1}'.format(k, type(v)))

        if k == 'operationId' and type(v) is not str:
            raise ValidationError('Invalid link object. "{0}" must be a str but was {1}'.format(k, type(v)))

        if k == 'description' and type(v) is not str:
            raise ValidationError('Invalid link object. "{0}" must be a str but was {1}'.format(k, type(v)))

        if k == 'server':
            validate_server_object(v)


def validate_servers_object(servers_object):
    if type(servers_object) is not list:
        raise ValidationError('Invalid server object. servers must be a list but was {0}'.format(type(servers_object)))
    for server_object in servers_object:
        validate_server_object(server_object)


def validate_server_object(server_object):
    if isinstance(server_object, dict):
        for k, v in server_object.items():
            if k not in constants.server_object_list:
                raise ValidationError('Invalid server object. Unknown field "{field}". See {url}'.format(
                    field=k,
                    url='https://swagger.io/specification/#ServerObject'))

            if k == 'variables':
                validate_server_variables_object(v)
                continue

            if k == 'url':
                if not validate_url(v):
                    raise ValidationError('Invalid url. See {url}'.format(
                        url='https://swagger.io/specification/#ServerObject'))

        if "url" not in server_object:
            raise ValidationError('Invalid server object. Missing field "url"')
    else:
        raise ValidationError('Invalid server object. See {url}'.format(
            url='https://swagger.io/specification/#ServerObject'
        ))


def validate_server_variables_object(server_variables_object):
    for k, v in server_variables_object.items():
        if k not in constants.server_variables_object_list:
            raise ValidationError('Invalid server variables object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='https://swagger.io/specification/#ServerVariablesObject'))

        if k == 'enum':
            if isinstance(v, list):
                if not all(isinstance(x, str) for x in v):
                    raise ValidationError(
                        'Invalid server variables object object. Each item of enum must be string'
                        'See https://swagger.io/specification/#ServerVariablesObject'
                    )
            else:
                raise ValidationError(
                    'Invalid server variables object object. Enum must be a list of strings'
                    'See https://swagger.io/specification/#ServerVariablesObject'
                )

    if 'default' not in server_variables_object:
        raise ValidationError(
            'Invalid server variables object object. Missing field "url"'
            'See https://swagger.io/specification/#ServerVariablesObject'
        )


def validate_map_example_object(map_example_object):
    for k, v in map_example_object.items():
        try:
            validate_reference_object(v)
        except ValidationError:
            validate_example_object(v)


def validate_example_object(example_object):
    for k, v in example_object.items():
        if k not in constants.example_object_list:
            raise ValidationError('Invalid example object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='https://swagger.io/specification/#ExampleObject'))

        if k == 'value':
            continue

        if k == 'summary' or k == 'description' or k == 'externalValue':
            if not type(v) == str:
                raise ValidationError('Invalid example object. "{0}" must be a str but was {1}'.format(k, type(v)))


def validate_tags(tag_list):
    if type(tag_list) is not list:
        raise ValidationError(f'Invalid tags object. "tags" must be a list but was {type(tag_list)}')
    for tag in tag_list:
        validate_tag_object(tag)


def validate_tag_object(tag_object):
    for k, v in tag_object.items():
        if k not in constants.tag_object_list:
            raise ValidationError('Invalid tag object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='https://swagger.io/specification/#TagObject'))

        if k == 'name' or k == 'description':
            if not type(v) == str:
                raise ValidationError('Invalid tag object. "{0}" must be a str but was {1}'.format(k, type(v)))

        if k == 'externalDocs':
            validate_external_documentation_object(v)

    if 'name' not in tag_object:
        raise ValidationError('Invalid tag object. Missing field "name"')


def validate_url(url):
    return re.match(constants.Regex.url, url) is not None


def validate_email(email):
    return re.match(constants.Regex.email, email) is not None


def validate_media_type(media_type):
    return re.match(constants.Regex.media_type, media_type) is not None


def extract_swagger_path(path):
    """
    Extracts a swagger type path from the given flask style path.
    This /path/<parameter> turns into this /path/{parameter}
    And this /<string(length=2):lang_code>/<string:id>/<float:probability>
    to this: /{lang_code}/{id}/{probability}
    """
    return re.sub(constants.Regex.path, "{\\1}", path), re.findall("<(.*?)>", path)


def sanitize_doc(comment):
    """
    Substitute HTML breaks for new lines in comment text.
    :param comment: The comment text
    :return: Sanitized comment text
    """
    if isinstance(comment, list):
        return sanitize_doc('\n'.join(filter(None, comment)))
    else:
        return comment.replace('\n', '<br/>') if comment else comment


def expected(schema, required=False):
    """
    decorator to add request body in method
    :param schema:
    :param required:
    :return:
    """

    def decorated(func):
        func.__request_body = {"schema": schema, "required": required}

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        return wrapper

    return decorated


def parameters(params=[]):
    """
    decorator to add multiple parameters to url

    Example usage:
        @parameters([
            {
                'in': 'query',
                'name': 'test',
                'schema': {type: integer},
                'description': 'a description'
            }])
        def get():
            ...


        @parameters(_in='query', name='test')
        def get():
            ...

    :param params:
    :return:
    """
    if not type(params) == list:
        raise ValidationError("decorator 'parameters' accept only list argument")

    for param in params:
        if param and param['in'] == 'path':
            raise ValidationError("""
            parameter with path must be set automlatically when added variable in url path
            example: api.add_resource(/user/<int:user_id>)
            """)

    def decorated(func):
        func_args = inspect.getfullargspec(func).args
        if "__params" in func.__dict__:
            for param in params:
                func.__params.append({k: v for k, v in dict(param).items()})

        else:
            func.__params = params

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if '_parser' in func_args:
                kwargs.update({'_parser': get_parser(params)})
            return func(self, *args, **kwargs)

        return wrapper

    return decorated


def parameter(param={}, **kwargs):
    """
    decorator to add one parameter to url

    Example usage:
        @parameter(_in='query', name='test', schema={type: integer}, description='a description')
        def get():
            ...

        @parameter({
                'in': 'query',
                'name': 'test',
                'schema': {type: integer},
                'description': 'a description'
            })
        def get():
            ...
    :param param
    :param kwargs:
    :return:
    """
    params = []
    if "_in" in kwargs:
        kwargs["in"] = kwargs.pop("_in")

    if not type(param) == dict:
        raise ValueError(f"'param' {param} must be of type 'dict'")

    if kwargs:
        params.append(dict(kwargs))

    if param:
        params.append(param)

    return parameters(params)


def response(response_code, description=None, summary=None, schema=None, no_content=False, example=None):
    """
    Decorator to add a response to the url
    :param response_code:
    :param description:
    :param summary:
    :param schema:
    :param no_content:
    :param example:
    :return:
    """

    def decorated(func):
        if "__response_code" in func.__dict__:
            func.__response_code.append(response_code)
        else:
            func.__response_code = [response_code]

        _description = description
        if not _description:
            _description = sanitize_doc(func.__doc__)
        if "__description" in func.__dict__:
            func.__description.append(sanitize_doc(_description))
        else:
            func.__description = [sanitize_doc(_description)]

        if "__summary" in func.__dict__:
            func.__summary.append(summary)
        else:
            func.__summary = [summary]

        if "__schema" in func.__dict__:
            func.__schema.append(schema)
        else:
            func.__schema = [schema]

        if "__no_content" in func.__dict__:
            func.__no_content.append(no_content)
        else:
            func.__no_content = [no_content]

        if "__custom_example" in func.__dict__:
            func.__custom_example.append(example)
        else:
            func.__custom_example = [example]

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        return wrapper

    return decorated


def reorder_with(schema, as_list: bool = False, response_code=200, description=None, summary=None, example=None):
    """
    Decorator to apply a schema to a response
    :param schema:
    :param as_list:
    :param response_code:
    :param description:
    :param example:
    :param summary:
    :return:
    """

    def decorated(func):
        _schema = [schema] if as_list else schema
        if "__schema" in func.__dict__:
            func.__schema.append(_schema)
        else:
            func.__schema = [_schema]

        if "__response_code" in func.__dict__:
            func.__response_code.append(response_code)
        else:
            func.__response_code = [response_code]

        _description = description
        if not _description:
            _description = sanitize_doc(func.__doc__)
        if "__description" in func.__dict__:
            func.__description.append(_description)
        else:
            func.__description = [_description]

        if "__summary" in func.__dict__:
            func.__summary.append(summary)
        else:
            func.__summary = [summary]

        if "__no_content" in func.__dict__:
            func.__no_content.append(False)
        else:
            func.__no_content = [False]

        _example = [example] if as_list else example
        if "__custom_example" in func.__dict__:
            func.__custom_example.append(_example)
        else:
            func.__custom_example = [_example]

        @wraps(func)
        def wrapper(self, *args, **kwargs):

            return func(self, *args, **kwargs)

        return wrapper

    return decorated


def reorder_list_with(schema, response_code=200, description=None, summary=None, example=None):
    """
    Same as reoder_with with as_list = True
    :param schema:
    :param response_code:
    :param description
    :param summary
    :param example
    :return:
    """
    return reorder_with(schema, True, response_code, description, summary, example)


def __tags_method(func, *_tags):
    """
    Decorate method
    :param func:
    :param _tags:
    :return:
    """
    func.__tags = list(_tags)

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **kwargs)

    return wrapper


def __tags_decorated_class(cls, *_tags):
    """
    Decorate each method of Resource class
    :param cls:
    :param _tags:
    :return:
    """
    for name, m in inspect.getmembers(cls, lambda x: inspect.isfunction(x) or inspect.ismethod(x)):
        if name in constants.operation_object_list:
            setattr(cls, name, __tags_method(m, *_tags))
    return cls


def tags(*_tags):
    """
    add tags to operation object
    :param _tags:
    :return:
    """

    def decorated(func_or_class):
        klass = None
        function = None

        if inspect.isclass(func_or_class):
            klass = func_or_class

        if inspect.ismethod(func_or_class) or inspect.isfunction(func_or_class):
            function = func_or_class

        if klass:
            return __tags_decorated_class(klass, *_tags)

        if function:
            return __tags_method(function, *_tags)

    return decorated


def reqparser(name, parser):
    """
    get reparser
    :param name:
    :param parser:
    :return:
    """

    def decorated(func):
        func.__reqparser = {"name": name, "parser": parser}

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        return wrapper

    return decorated


def slash_join(*args):
    """
    Function to join several parts of url
    :param args:
    :return:
    """
    return "/".join([url[:-1] if url.endswith("/") else url for url in args]).replace('//', '/')


def payload():
    """
    Return the request response
    :return:
    """
    return request.get_json()
