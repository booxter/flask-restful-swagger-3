from flask_restful_swagger_3 import Schema


def email_model():
    class EmailModel(Schema):
        type = 'string'
        format = 'email'

    return EmailModel


def model_to_parse():
    class ModelToParse(Schema):
        type = 'string'
        default = 'testing'

    return ModelToParse


def keys_model():
    class KeysModel(Schema):
        type = 'string'

    return KeysModel


def p_model():
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
            'mail': email_model(),
            'keys': keys_model().array()
        }
        required = ['name', 'keys']

    return PModel


def user_model():
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

    return UserModel


def swagger_test_model():
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

    return SwaggerTestModel


def schema_test_model():
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

    return SchemaTestModel



def property_schema():
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

    return Property


def category_schema():
    class Category(Schema):
        type = 'object'
        properties = {
            'id': {
                'type': 'integer'
            },
            'name': {
                'type': 'string'
            },
            'property': property_schema()
        }
        required = ['id', 'name']

    return Category


def nested_schema():
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
            'category': category_schema(),
            'mail': email_model()
        }
        required = ['id']

    return NestedSchema


def enum_schema():
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

    return EnumSchema


def enum_schema_set():
    class EnumSchemaSet(Schema):
        type = 'object'
        properties = {
            'my_choice': {
                'type': 'string',
                'enum': {'choice_1', 'choice_2'}
            }
        }

    return EnumSchemaSet


def enum_schema_tuple():
    class EnumSchemaTuple(Schema):
        type = 'object'
        properties = {
            'my_choice': {
                'type': 'string',
                'enum': ('choice_1', 'choice_2')
            }
        }

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
    class SuperSchema(Schema):
        type = 'object'
        properties = {
            'id': {'type': 'string'},
            'super_attribute': {'type': 'string'},
            'other_attribute': {'type': 'string'}
        }
        required = ['other_attribute']

    return SuperSchema


def bad_super_schema():
    class BadSuperSchema(Schema):
        type = 'string'

    return BadSuperSchema


def super_schema_without_type():
    class SuperSchemaWithoutType(Schema):
        properties = {
            'id': {'type': 'string'},
            'super_attribute': {'type': 'string'},
            'other_attribute': {'type': 'string'}
        }
        required = ['other_attribute']

    return SuperSchemaWithoutType


def sub_schema():
    class SubSchema(super_schema()):
        properties = {
            'sub_attribute': {'type': 'string'}
        }
        required = ['sub_attribute']

    return SubSchema


def sub_schema_without_required():
    class SubSchema(super_schema()):
        properties = {
            'sub_attribute': {'type': 'string'}
        }

    return SubSchema


def sub_schema_empty():
    class SubSchemaEmpty(super_schema()):
        pass

    return SubSchemaEmpty


def bad_sub_schema():
    class BadSubSchema(super_schema()):
        type = 'string'
    return BadSubSchema


def sub_schema_with_bad_super_schema():
    class SubSchemaWithBadSuperSchema(bad_super_schema()):
        pass
    return SubSchemaWithBadSuperSchema


def sub_schema_with_super_schema_without_type():
    class SubSchemaWithSuperSchemaWithoutType(super_schema_without_type()):
        properties = {
            'sub_attribute': {'type': 'string'}
        }
        required = ['sub_attribute']
    return SubSchemaWithSuperSchemaWithoutType


def schema_with_array():
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


def nullable_schema():
    class NullableSchema(Schema):
        type = 'object'
        properties = {
            'nullable_str': {'type': 'string', 'nullable': 'true'},
            'nullable_int': {'type': 'integer', 'nullable': 'true'}
        }
        required = ['nullable_str', 'nullable_int']

    return NullableSchema


def bad_nullable_schema():
    class NullableSchema(Schema):
        type = 'object'
        properties = {
            'nullable_str': {'type': 'string', 'nullable': 'other'},
            'nullable_int': {'type': 'integer', 'nullable': 'true'}
        }
        required = ['nullable_str', 'nullable_int']

    return NullableSchema
