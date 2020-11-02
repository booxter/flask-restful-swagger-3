from flask_restful_swagger_3 import Schema


class EmailModel(Schema):
    type = 'string'
    format = 'email'


class ModelToParse(Schema):
    type = 'string'
    default = 'testing'


class KeysModel(Schema):
    type = 'string'


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
    required = ['name', 'keys']


class UserModel(Schema):
    type = 'object'
    properties = {
        'id': {
            'type': 'integer',
            'format': 'int64',
        },
        'name': {
            'type': 'string'
        },
        'password': {
            'type': 'string',
            'nullable': 'true',
            'load_only': 'true'
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
        },
        'number': {
            'type': 'number'
        },
        'boolean': {
            'type': 'boolean'
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


class EnumSchema(Schema):
    """
    Test nested schema model.
    """
    type = 'object'
    properties = {
        'my_choice': {
            'type': 'string',
            'enum': ['choice_1', 'choice_2']
        }
    }


class EnumSchemaSet(Schema):
    type = 'object'
    properties = {
        'my_choice': {
            'type': 'string',
            'enum': {'choice_1', 'choice_2'}
        }
    }


class EnumSchemaTuple(Schema):
    type = 'object'
    properties = {
        'my_choice': {
            'type': 'string',
            'enum': ('choice_1', 'choice_2')
        }
    }


class SuperSchema(Schema):
    type = 'object'
    properties = {
        'id': {'type': 'string'},
        'super_attribute': {'type': 'string'},
        'other_attribute': {'type': 'string'}
    }
    required = ['other_attribute']


class BadSuperSchema(Schema):
    type = 'string'


class SuperSchemaWithoutType(Schema):
    properties = {
        'id': {'type': 'string'},
        'super_attribute': {'type': 'string'},
        'other_attribute': {'type': 'string'}
    }
    required = ['other_attribute']


class SubSchema(SuperSchema):
    properties = {
        'sub_attribute': {'type': 'string'}
    }
    required = ['sub_attribute']


class SubSchemaWithoutRequired(SuperSchema):
    properties = {
        'sub_attribute': {'type': 'string'}
    }


class SubSchemaWithSuperSchemaWithoutType(SuperSchemaWithoutType):
    properties = {
        'sub_attribute': {'type': 'string'}
    }
    required = ['sub_attribute']


class ArraySchema(Schema):
    type = 'object'
    properties = {
        'id': {'type': 'integer'},
        'prop1': {'type': 'string'},
        'prop2': {'type': 'string'}
    }
    required = ['prop1']


class TestSchema(Schema):
    type = 'object'
    properties = {
        'id': {'type': 'integer'},
        'name': {'type': 'string'},
        'my_test_array': ArraySchema.array()
    }


class NullableSchema(Schema):
    type = 'object'
    properties = {
        'nullable_str': {'type': 'string', 'nullable': 'true'},
        'nullable_int': {'type': 'integer', 'nullable': 'true'}
    }
    required = ['nullable_str', 'nullable_int']


def email_model():
    return EmailModel


def model_to_parse():
    return ModelToParse


def keys_model():
    return KeysModel


def p_model():
    return PModel


def user_model():
    return UserModel


def swagger_test_model():
    return SwaggerTestModel


def schema_test_model():
    return SchemaTestModel


def property_schema():
    return Property


def category_schema():
    return Category


def nested_schema():
    return NestedSchema


def enum_schema():
    return EnumSchema


def enum_schema_set():
    return EnumSchemaSet


def enum_schema_tuple():
    return EnumSchemaTuple


def bad_enum_schema():
    class BadEnumSchema(Schema):
        type = 'object'
        properties = {
            'my_choice': {
                'type': 'string',
                'enum': 'choice1'
            }
        }

    return BadEnumSchema


def bad_enum_schema_type():
    class BadEnumSchemaType(Schema):
        type = 'object'
        properties = {
            'my_choice': {
                'type': 'string',
                'enum': ['choice1', 2]
            }
        }

    return BadEnumSchemaType


def super_schema():
    return SuperSchema


def bad_super_schema():
    return BadSuperSchema


def super_schema_without_type():
    return SuperSchemaWithoutType


def sub_schema():
    return SubSchema


def sub_schema_without_required():
    return SubSchemaWithoutRequired


def sub_schema_empty():
    class SubSchemaEmpty(super_schema()):
        pass

    return SubSchemaEmpty


def bad_sub_schema():
    class BadSubSchema(SuperSchema):
        type = 'string'

    return BadSubSchema


def sub_schema_with_bad_super_schema():
    class SubSchemaWithBadSuperSchema(BadSuperSchema):
        pass

    return SubSchemaWithBadSuperSchema


def sub_schema_with_super_schema_without_type():
    return SubSchemaWithSuperSchemaWithoutType


def schema_with_array():
    return TestSchema


def nullable_schema():
    return NullableSchema


def bad_nullable_schema():
    class BadNullableSchema(Schema):
        type = 'object'
        properties = {
            'nullable_str': {'type': 'string', 'nullable': 'other'},
            'nullable_int': {'type': 'integer', 'nullable': 'true'}
        }
        required = ['nullable_str', 'nullable_int']

    return BadNullableSchema
