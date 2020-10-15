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


class Property(Schema):
    type = 'object'
    properties = {
        'property1': {
            'type': 'string',
        },
        'property2': {
            'type': 'string',
        }
    }


class Category(Schema):
    type = 'object'
    properties = {
        'id': {
            'type': 'integer'
        },
        'name': {
            'type': 'string'
        },
        'property': Property
    }
    required = ['id', 'name']


class NestedSchema(Schema):
    """
    Test nested schema model.
    """
    type = 'object'
    properties = {
        'id': {
            'type': 'integer'
        },
        'name': {
            'type': 'string'
        },
        'category': Category,
        'mail': EmailModel
    }
    required = ['id']


def fixture_nested_obj():
    return {
        'id': 1,
        'name': 'fake',
        'category': {
            'id': 1,
            'name': 'fake category',
            'property': {
                'property1': 'fake',
                'property2': 'fake'
            }
        },
        'mail': 'tes@test.fr'
    }


def fixture_bad_type_in_nested_obj():
    return {
        'id': 1,
        'name': 'fake',
        'category': {
            'id': 1,
            'name': 'fake category',
            'property': {
                'property1': 2,
                'property2': 'fake'
            }
        }
    }