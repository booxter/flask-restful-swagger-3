import collections
import re
import inspect
import copy
from functools import wraps

from flask import request
from flask_restful import Resource, reqparse, inputs


class ValidationError(ValueError):
    pass


def auth(api_key, endpoint, method):
    """Override this function in your application.

    If this function returns False, 401 forbidden is raised and the documentation is not visible.
    """
    return True


def _auth(*args, **kwargs):
    return auth(*args, **kwargs)


def create_swagger_endpoint(swagger_object):
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
        # ('host', '', 'host'),
        # ('base_path', '', 'basePath'),
        # ('schemes', [], 'schemes'),
        ('servers', [], 'servers'),
        # ('consumes', [], 'consumes'),
        # ('produces', [], 'produces'),
        # ('parameters', {}, 'parameters'),
        # ('responses', {}, 'responses'),
        # ('security_definitions', {}, 'securityDefinitions'),
        # ('security', [], 'security'),
        # ('tags', [], 'tags'),
        # ('external_docs', {}, 'externalDocs'),
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
    if 'schema' not in param:
        return None
    param = param['schema']
    param_type = param.get('type', None)
    if param_type:
        if param_type == 'array':
            if 'items' in param:
                param = param['items']
            param_type = param.get('type', None)
        if param_type == 'string':
            param_format = param.get('format', None)

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
    if 'schema' in param:
        param_type = param['schema'].get('type', None)

        if param_type == 'array':
            return 'append'
        return 'store'

    return None


def get_parser_arg(param):
    """
    Return an argument for the request parser.
    :param param: Swagger document parameter
    :return: Request parser argument
    """
    return (
        param['name'],
        {
            'dest': param['name'],
            'type': get_data_type(param),
            'location': 'args',
            'help': param.get('description', None),
            'required': param.get('required', False),
            'default': param.get('default', None),
            'action': get_data_action(param)
        })


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
        parser.add_argument(arg[0], **arg[1])

    return parser


def doc(operation_object):
    """Decorator to save the documentation of an api endpoint.

    Saves the passed arguments as an attribute to use them later when generating the swagger spec.
    """
    def decorated(f):
        f.__swagger_operation_object = copy.deepcopy(operation_object)

        @wraps(f)
        def inner(self, *args, **kwargs):
            # Get names of resource function arguments

            func_args = inspect.getfullargspec(f).args
            # You can also use
            # func_args = list(inspect.signature(f).parameters.keys())

            # Add a parser for query arguments if the special argument '_parser' is present
            if 'parameters' in f.__swagger_operation_object and '_parser' in func_args:
                kwargs.update({'_parser': get_parser(f.__swagger_operation_object['parameters'])})

            return f(self, *args, **kwargs)

        return inner
    return decorated


def validate_info_object(info_object):
    for k, v in info_object.items():
        if k not in ['title', 'description', 'termsOfService', 'contact', 'license', 'version']:
            raise ValidationError('Invalid info object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='http://swagger.io/specification/#infoObject'))

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
            if k not in ['name', 'url', 'email']:
                raise ValidationError('Invalid contact object. Unknown field "{field}". See {url}'.format(
                    field=k,
                    url='http://swagger.io/specification/#contactObject'))

            if k == 'email':
                validate_email(v)
                continue


def validate_license_object(license_object):
    if license_object:
        for k, v in license_object.items():
            if k not in ['name', 'url']:
                raise ValidationError('Invalid license object. Unknown field "{field}". See {url}'.format(
                    field=k,
                    url='http://swagger.io/specification/#licenseObject'))

            if k ==  'url':
                validate_url(v)
                continue

        if 'name' not in license_object:
            raise ValidationError('Invalid license object. Missing field "name"')


def validate_path_item_object(path_item_object):
    """Checks if the passed object is valid according to http://swagger.io/specification/#pathItemObject"""

    for k, v in path_item_object.items():
        if k == '$ref':
            continue
        if k in ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace']:
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
                url='http://swagger.io/specification/#pathItemObject'))


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
            validate_external_documentation_object(v) # to check
            continue
        if k in ['parameters']:
            for parameter in v:
                validate_parameter_object(parameter)
            continue
        if k in ['responses']:
            validate_responses_object(v)
            continue
        if k in ['security']:
            validate_security_requirement_object(v)
            continue
        raise ValidationError('Invalid operation object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='http://swagger.io/specification/#pathItemObject'))
    if 'responses' not in operation_object:
        raise ValidationError('Invalid operation object. Missing field "responses"')


def validate_parameter_object(parameter_object):
    for k, v in parameter_object.items():
        if k not in ['name', 'in', 'description', 'required', 'deprecated', 'allowEmptyValue', 'style', 'explode',
                     'allowReserved', 'schema', 'example', 'examples', 'content', 'matrix', 'label', 'form',
                     'simple', 'spaceDelimited', 'pipeDelimited', 'deepObject', 'reqparser']:
            raise ValidationError('Invalid parameter object. Unknown field "{field}". See {url}'.format(
                    field=k,
                    url='http://swagger.io/specification/#parameterObject'))
    if 'reqparser' in parameter_object:
        if 'name' not in parameter_object['reqparser']:
            raise ValidationError('name for request parser not specified')
        if 'parser' not in parameter_object['reqparser'] or not isinstance(parameter_object['reqparser']['parser'], reqparse.RequestParser):
            raise ValidationError('RequestParser object not specified')
        return
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


def validate_reference_object(parameter_object):
    if len(parameter_object.keys()) > 1 or '$ref' not in parameter_object:
        raise ValidationError('Invalid reference object. It may only contain key "$ref"')


def validate_external_documentation_object(external_documentation_object):
    pass


def validate_responses_object(responses_object):
    for k, v in responses_object.items():
        if k in ["1XX", "2XX", "3XX", "4XX", "5XX", "default"]:
            try:
                validate_reference_object(v)
            except ValidationError:
                validate_response_object(v)
            continue
        if 99 < int(k) < 600:
            try:
                validate_reference_object(v)
            except ValidationError:
                validate_response_object(v)
                continue


def validate_response_object(response_object):
    for k, v in response_object.items():
        if k == 'description':
            continue
        if k == 'headers':
            try:
                validate_reference_object(v)
            except ValidationError:
                validate_headers_object(v)
            continue
        if k == 'content':
            validate_content_object(v)
            continue
        if k == "links":
            validate_link_object(v)
            continue
        raise ValidationError('Invalid response object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='http://swagger.io/specification/#responseObject'))
    if 'description' not in response_object:
        raise ValidationError('Invalid response object. Missing field "description"')


def validate_request_body_object(request_body_object):
    for k, v in request_body_object.items():
        if k in ['description']:
            continue
        if k in ['required']:
            if isinstance(v, bool):
                continue
        if k in ['content']:
            validate_content_object(v)
            continue

    if 'content' not in request_body_object:
        raise ValidationError('Invalid request body object. Missing field "content"')


def validate_content_object(content_object):
    for k, v in content_object.items():
        if re.match(r'(.*)/(.*)', k):
            validate_media_type_object(v)
            continue
        raise ValidationError(
            'Invalid content object, the field must match the following patter ("application/json", "*/*" ...").'
            '. See http://swagger.io/specification/#mediaObject'
        )


def validate_media_type_object(media_type_object):
    for k, v in media_type_object.items():
        if k == "schema":
            validate_schema_object(v)
            continue
        if k == "examples":
            validate_example_object(v)
            continue


def validate_security_requirement_object(security_requirement_object):
    pass


def validate_components_object(definition_object):
    for k, v in definition_object.items():
        if k == "schemas":
            validate_schema_object(v)
            continue


def validate_schema_object(schema_object):
    for k, v in schema_object.items():
        try:
            validate_reference_object(v)
            continue
        except AttributeError:
            if k == 'required' and not isinstance(v, list):
                raise ValidationError('Invalid schema object. "{0}" must be a list but was {1}'.format(k, type(v)))


def validate_headers_object(headers_object):
    for k, v in headers_object.items():
        if k not in ['name', 'in', 'description', 'required', 'deprecated', 'allowEmptyValue', 'style', 'explode',
                     'allowReserved', 'schema', 'example', 'examples', 'content', 'matrix', 'label', 'form',
                     'simple', 'spaceDelimited', 'pipeDelimited', 'deepObject']:
            raise ValidationError('Invalid headers object. Unknown field "{field}". See {url}'.format(
                    field=k,
                    url='http://swagger.io/specification/#headerObject'))
        if k == 'name':
            raise ValidationError('"name" must not be specified. See http://swagger.io/specification/#headerObject')
        if k == 'in':
            raise ValidationError('"in" must not be specified. See http://swagger.io/specification/#headerObject')

        if k == 'schema':
            validate_schema_object(headers_object['schema'])
            continue


def validate_link_object(link_object):
    for k, v in link_object.items():
        if k in ['operationRef', 'operationId', 'parameters', 'requestBody', 'description']:
            continue
        if k == 'server':
            validate_servers_object(v)


def validate_servers_object(server_object):
    if isinstance(server_object, list):
        for server in server_object:
            validate_server_object(server)

    else:
        validate_server_object(server_object)


def validate_server_object(server_object):
    if isinstance(server_object, dict):
        for k, v in server_object.items():
            if k not in ['url', 'description', 'variables']:
                raise ValidationError('Invalid server object. Unknown field "{field}". See {url}'.format(
                    field=k,
                    url='http://swagger.io/specification/#serverObject'))

            if k == 'variables':
                validate_server_variables_object(v)
                continue

            if k == 'url':
                if not validate_url(v):
                    raise ValidationError('Invalid url. See {url}'.format(
                        url='http://swagger.io/specification/#serverObject'))

        if "url" not in server_object:
            raise ValidationError('Invalid server object. Missing field "url"')
    else:
        raise ValidationError('Invalid server object. See {url}'.format(
            url='http://swagger.io/specification/#serverObject'
        ))


def validate_url(url):
    url_regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(url_regex, url) is not None


def validate_email(email):
    email_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'  # quoted-string
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain

    return re.match(email_regex, email) is not None


def validate_server_variables_object(server_variables_object):
    for k, v in server_variables_object.items():
        if k not in ['enum', 'default', 'description']:
            raise ValidationError('Invalid server variables object. Unknown field "{field}". See {url}'.format(
                field=k,
                url='http://swagger.io/specification/#headerObject'))

        if k == 'enum':
            if isinstance(v, list):
                if not all(isinstance(x, str) for x in v):
                    raise ValidationError(
                        'Invalid server variables object object. Each item of enum must be string'
                        'See http://swagger.io/specification/#serverVariablesObject'
                    )
            else:
                raise ValidationError(
                    'Invalid server variables object object. Enum must be a list of strings'
                    'See http://swagger.io/specification/#serverVariablesObject'
                )

    if 'default' not in server_variables_object:
        raise ValidationError(
            'Invalid server variables object object. Missing field "url"'
            'See http://swagger.io/specification/#serverVariablesObject'
        )


def validate_example_object(example_object):
    pass


def extract_swagger_path(path):
    """
    Extracts a swagger type path from the given flask style path.
    This /path/<parameter> turns into this /path/{parameter}
    And this /<string(length=2):lang_code>/<string:id>/<float:probability>
    to this: /{lang_code}/{id}/{probability}
    """
    return re.sub('<(?:[^:]+:)?([^>]+)>', '{\\1}', path)


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


def parse_method_doc(method, operation):
    """
    Parse documentation from a resource method.
    :param method: The resource method
    :param operation: The operation document
    :return: The operation summary
    """
    summary = None

    full_doc = inspect.getdoc(method)
    if full_doc:
        lines = full_doc.split('\n')
        if lines:
            # Append the first line of the docstring to any summary specified
            # in the operation document
            summary = sanitize_doc([operation.get('summary', None), lines[0]])

    return summary


def parse_schema_doc(cls, definition):
    """
    Parse documentation from a schema class.
    :param cls: The schema class
    :param definition: The schema definition
    :return: The schema description
    """
    description = None

    # Skip processing the docstring of the schema class if the schema
    # definition already contains a description
    if 'description' not in definition:
        full_doc = inspect.getdoc(cls)

        # Avoid returning the docstring of the base dict class
        if full_doc and full_doc != inspect.getdoc(dict):
            lines = full_doc.split('\n')
            if lines:
                # Use the first line of the class docstring as the description
                description = sanitize_doc(lines[0])

    return description
