from http import HTTPStatus
import re

info_object_list = ['title', 'description', 'termsOfService', 'contact', 'license', 'version']

contact_object_list = ['name', 'url', 'email']

license_object_list = ['name', 'url']

parameter_object_list = ['name', 'in', 'description', 'required', 'deprecated', 'allowEmptyValue',
                         'style', 'explode', 'allowReserved', 'schema', 'example', 'examples', 'content', 'matrix',
                         'label', 'form', 'simple', 'spaceDelimited', 'pipeDelimited', 'deepObject']

http_status_enum = [status for status in HTTPStatus]
http_status_value = [status.value for status in HTTPStatus]
responses_object_list = list(set(http_status_enum + http_status_value))

operation_object_list = ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace']

security_scheme_list = ['type', 'description', 'name', 'in', 'scheme', 'bearerFormat', 'flows', 'openIdConnectUrl']

security_scheme_object_scheme_list = ['basic', 'bearer', 'digest', 'HOBA', 'mutual', 'negotiate',
                                      'oauth', 'SCRAM-SHA-1', 'SCRAM-SHA-256', 'vapid']


security_scheme_object_type_list = ["apiKey", "http", "oauth2", "openIdConnect"]

oauth_flows_object_list = ['implicit', 'password', 'clientCredentials', 'authorizationCode']

oauth_flows_object_sub_level_list = ['authorizationUrl', 'tokenUrl', 'refreshUrl', 'scopes']

components_object_list = ['schemas', 'responses', 'parameters', 'examples', 'requestBodies',
                          'headers', 'securitySchemes', 'links', 'callbacks']


headers_object_list = ['name', 'in', 'description', 'required', 'deprecated', 'allowEmptyValue', 'style', 'explode',
                       'allowReserved', 'schema', 'example', 'examples', 'content', 'matrix', 'label', 'form',
                       'simple', 'spaceDelimited', 'pipeDelimited', 'deepObject']

link_object_list = ['operationRef', 'operationId', 'parameters', 'requestBody', 'description', 'server']


server_object_list = ['url', 'description', 'variables']


server_variables_object_list = ['enum', 'default', 'description']


example_object_list = ['summary', 'description', 'value', 'externalValue']


open_api_object_list = ['openapi', 'info', 'servers', 'paths', 'components', 'security', 'tags', 'externalDocs']


tag_object_list = ['name', 'description', 'externalDocs']


external_doc_object_list = ['description', 'url']


class TypeSwagger:
    bool = "boolean"
    str = "string"
    float = "number"
    int = "integer"
    bin = "binary"
    list = "array"
    dict = "object"

    @classmethod
    def get_type(cls, _type):
        if _type in cls.__dict__:
            return cls.__dict__[_type]


class Regex:
    email = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'  # quoted-string
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain

    url = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    path = r"<(?:[^:]+:)?([^>]+)>"

    media_type = re.compile(r"[a-zA-Z0-9!#$%^&\*_\+{}\|'.`~]+/[a-zA-Z0-9!#$%^&\*_\+{}\|'.; =`~-]+", re.IGNORECASE)
