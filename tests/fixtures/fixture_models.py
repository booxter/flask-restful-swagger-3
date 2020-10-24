from flask_restful_swagger_3 import Schema


class EmailModel(Schema):
    type = 'string'
    format = 'email'


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


def fixture_pmodel():
    return PModel


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


def fixture_user_model():
    return UserModel


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


def fixture_swagger_test_model():
    return SwaggerTestModel


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


def fixture_schema_test_model():
    return SchemaTestModel


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


def fixture_nested_schema():
    return NestedSchema


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


def fixture_enum_schema():
    return EnumSchema


class EnumSchemaSet(Schema):
    type = 'object'
    properties = {
        'my_choice': {
            'type': 'string',
            'enum': {'choice_1', 'choice_2'}
        }
    }


def fixture_enum_schema_set():
    return EnumSchemaSet


class EnumSchemaTuple(Schema):
    type = 'object'
    properties = {
        'my_choice': {
            'type': 'string',
            'enum': ('choice_1', 'choice_2')
        }
    }


def fixture_enum_schema_tuple():
    return EnumSchemaTuple


class BadEnumSchema(Schema):
    type = 'object'
    properties = {
        'my_choice': {
            'type': 'string',
            'enum': 'choice1'
        }
    }


def fixture_bad_enum_schema():
    return BadEnumSchema


class BadEnumSchemaType(Schema):
    type = 'object'
    properties = {
        'my_choice': {
            'type': 'string',
            'enum': ['choice1', 2]
        }
    }


def fixture_bad_enum_schema_type():
    return BadEnumSchemaType


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


class SubSchemaEmpty(SuperSchema):
    pass


def fixture_sub_schema():
    return SubSchema


def fixture_sub_schema_empty():
    return SubSchemaEmpty


def fixture_bad_sub_schema():
    class BadSubSchema(SuperSchema):
        type = 'string'
    return BadSubSchema


def fixture_sub_schema_with_bad_super_schema():
    class SubSchemaWithBadSuperSchema(BadSuperSchema):
        pass
    return SubSchemaWithBadSuperSchema


def fixture_sub_schema_with_super_schema_without_type():
    class SubSchemaWithSuperSchemaWithoutType(SuperSchemaWithoutType):
        properties = {
            'sub_attribute': {'type': 'string'}
        }
        required = ['sub_attribute']
    return SubSchemaWithSuperSchemaWithoutType


def fixture_schema_with_array():
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

    return TestSchema


def fixture_nullable_schema():
    class NullableSchema(Schema):
        type = 'object'
        properties = {
            'nullable_str': {'type': 'string', 'nullable': 'true'},
            'nullable_int': {'type': 'integer', 'nullable': 'true'}
        }
        required = ['nullable_str', 'nullable_int']

    return NullableSchema


def fixture_bad_nullable_schema():
    class NullableSchema(Schema):
        type = 'object'
        properties = {
            'nullable_str': {'type': 'string', 'nullable': 'other'},
            'nullable_int': {'type': 'integer', 'nullable': 'true'}
        }
        required = ['nullable_str', 'nullable_int']

    return NullableSchema
