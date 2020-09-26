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


class PModel(Schema):
    type = 'object'
    properties = {
        'id': {
            'type': 'integer',
            'format': 'int64',
        },
        'name': {
            'type': 'string'
        },
        'mail': EmailModel,
        'keys': KeysModel.array()
    }
    required = ['name']


class UserModel(Schema):
    type = 'object'
    properties = {
        'id': {
            'type': 'integer',
            'format': 'int64',
        },
        'name': {
            'type': 'string'
        }
    }
    required = ['name']


class SwaggerTestModel(Schema):
    """
    Test schema model.
    """
    type = 'object'
    properties = {
        'id': {
            'type': 'string'
        }
    }


class SchemaTestModel(Schema):
    """
    Test schema model.
    """
    type = 'object'
    properties = {
        'id': {
            'type': 'integer'
        },
        'name': {
            'type': 'string'
        }
    }
    required = ['id']
