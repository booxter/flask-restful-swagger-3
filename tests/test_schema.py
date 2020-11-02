import pytest
from flask_restful_swagger_3.exceptions import SchemaAlreadyExist

from flask_restful_swagger_3 import Schema


class TestSchema:
    def test_should_validate_schema_valid(self, schema_test_model):
        assert schema_test_model(**{'id': 1, 'name': 'somebody'}) == {'id': 1, 'name': 'somebody'}

    def test_should_validate_schema_missing_required(self, schema_test_model):
        with pytest.raises(ValueError):
            schema_test_model(**{'name': 'somebody'})

    def test_should_validate_schema_invalid_type(self, schema_test_model):
        with pytest.raises(ValueError) as e:
            schema_test_model(**{'id': '1'})

        assert str(e.value) == 'The attribute "id" must be an int, but was "<class \'str\'>"'

        with pytest.raises(ValueError) as e:
            schema_test_model(**{'id': 1, 'name': 1})

        assert str(e.value) == 'The attribute "name" must be a string, but was "<class \'int\'>"'

        with pytest.raises(ValueError) as e:
            schema_test_model(**{'id': 1, 'name': 'name', 'number': 'n'})

        assert str(e.value) == 'The attribute "number" must be an int or float, but was "<class \'str\'>"'

        with pytest.raises(ValueError) as e:
            schema_test_model(**{'id': 1, 'name': 'name', 'number': 2.5, 'boolean': 'string'})

        assert str(e.value) == 'The attribute "boolean" must be a bool, but was "<class \'str\'>"'

        class Sch(Schema):
            type = 'object'
            properties = {
                'list': schema_test_model.array()
            }

        with pytest.raises(ValueError) as e:
            Sch(**{'list': [
                {'id': 1, 'name': 'name', 'number': 2.5, 'boolean': 'string'}
            ]})

        assert str(e.value) == 'The attribute "boolean" must be a bool, but was "<class \'str\'>"'

        class Enum(Schema):
            type = 'object'
            properties = {
                'enum': {
                    'type': 'string',
                    'enum': ['1', '2']
                }
            }

        with pytest.raises(ValueError) as e:
            Enum(**{'enum': 2})

        assert str(e.value) == 'The attribute "enum" must be a string, but was "<class \'int\'>"'

    def test_should_validate_nested_schema_ok(self, nested_schema, nested_obj):
        nested_schema(**nested_obj)

    def test_should_no_validate_nested_schema_invalid_type(self, nested_schema, bad_type_in_nested_obj):
        with pytest.raises(ValueError):
            nested_schema(**bad_type_in_nested_obj)

    def test_should_validate_shema_with_enum_list_ok(self, enum_schema, enum_obj):
        enum_schema(**enum_obj)

    def test_should_validate_shema_with_enum_set_ok(self, enum_schema_set, enum_obj):
        enum_schema_set(**enum_obj)

    def test_should_validate_shema_with_enum_tuple_ok(self, enum_schema_tuple, enum_obj):
        enum_schema_tuple(**enum_obj)

    def test_should_raise_error_when_enum_has_bad_type(self, bad_enum_schema, enum_obj):
        with pytest.raises(TypeError):
            bad_enum_schema(**enum_obj)

    def test_should_not_validate_shema_with_enum_not_in_choice(self, enum_schema, enum_obj_not_in_choice):
        with pytest.raises(ValueError):
            enum_schema(**enum_obj_not_in_choice)

    def test_should_not_validate_shema_with_enum_item_bad_type(self, bad_enum_schema_type, enum_obj):
        with pytest.raises(ValueError):
            bad_enum_schema_type(**enum_obj)

    def test_should_validate_obj_with_sub_schema(self, sub_schema, obj_of_sub_schema):
        assert sub_schema(**obj_of_sub_schema)

    def test_sub_schema_has_required_of_parent(self, sub_schema_without_required):
        assert sub_schema_without_required.required == ['other_attribute']

    def test_should_valdate_definitions_of_sub_schema(self, sub_schema, expected_definition_of_sub_schema):
        assert sub_schema.definitions()['properties'] == expected_definition_of_sub_schema['properties']
        for required in sub_schema.definitions()['required']:
            assert required in expected_definition_of_sub_schema['required']

    def test_should_valdate_example_of_sub_schema(self, sub_schema, expected_example_of_sub_schema):
        assert sub_schema.example() == expected_example_of_sub_schema

    def test_should_valdate_example_of_sub_schema_empty(self, sub_schema_empty, expected_example_of_sub_schema):
        del expected_example_of_sub_schema['sub_attribute']
        assert sub_schema_empty.example() == expected_example_of_sub_schema

    def test_should_raise_error_when_create_sub_schema_with_different_type(
            self, bad_sub_schema):
        with pytest.raises(TypeError):
            bad_sub_schema()

    def test_should_raise_error_when_create_sub_schema_with_bad_super_schema(
            self, sub_schema_with_bad_super_schema):
        with pytest.raises(TypeError):
            sub_schema_with_bad_super_schema()

    def test_should_create_schema_when__super_schema_has_no_type(
            self, sub_schema_with_super_schema_without_type):
        sub_schema_with_super_schema_without_type()

    def test_should_validate_array_schema_object_ok(self, schema_with_array, object_with_array):
        schema_with_array(**object_with_array)

    def test_should_validate_array_schema_object_example(self, schema_with_array):
        assert schema_with_array.example() == {
            'id': 'integer',
            'my_test_array': [
                {
                    'id': 'integer',
                    'prop1': 'string',
                    'prop2': 'string'
                }
            ],
            'name': 'string'
        }

    def test_should_raise_error_when_array_schema_object_bad_type(self, schema_with_array, object_with_array):
        object_with_array["my_test_array"] = "test"
        with pytest.raises(ValueError):
            schema_with_array(**object_with_array)

    def test_should_raise_error_when_array_schema_object_bad_item_type(self, schema_with_array, object_with_array):
        object_with_array["my_test_array"][0]["prop1"] = 1
        with pytest.raises(ValueError):
            schema_with_array(**object_with_array)

    def test_should_raise_error_when_array_schema_object_item_not_exist(self, schema_with_array, object_with_array):
        object_with_array["my_test_array"][0]["not_exist"] = "not_exist"
        with pytest.raises(ValueError):
            schema_with_array(**object_with_array)

    def test_should_validate_array_schema_ok(self, p_model):
        object_with_string_array = {
            "name": "test",
            "keys": ["keys1", "keys2"]
        }
        p_model(**object_with_string_array)

    def test_should_raise_error_when_array_has_all_bad_type(self, p_model):
        object_with_string_array = {
            "name": "test",
            "keys": [1, 2]
        }
        with pytest.raises(ValueError):
            p_model(**object_with_string_array)

    def test_should_raise_error_when_array_has_some_bad_type(self, p_model):
        object_with_string_array = {
            "name": "test",
            "keys": ["keys1", 2]
        }
        with pytest.raises(ValueError):
            p_model(**object_with_string_array)

    def test_should_validate_nullable_schema_ok(self, nullable_schema):
        nullable_object = {
            "nullable_str": None,
            "nullable_int": None
        }
        nullable_schema(**nullable_object)

    def test_should_raise_error_when_nullable_schema_are_not_null_and_bad_type(self, nullable_schema):
        nullable_object = {
            "nullable_str": 1,
            "nullable_int": "other"
        }
        with pytest.raises(ValueError):
            nullable_schema(**nullable_object)

    def test_should_raise_error_when_nullable_is_set_incorrectly(self, bad_nullable_schema):
        nullable_object = {
            "nullable_str": None,
            "nullable_int": None
        }
        with pytest.raises(ValueError):
            bad_nullable_schema(**nullable_object)

    def test_schema_password_with_load_only(self):
        class Password(Schema):
            type = 'object'
            properties = {
                'name': {
                    'type': 'string',
                },
                'pass': {
                    'type': 'string',
                    'format': 'password',
                    'load_only': 'true'
                }
            }
        assert Password(**{'name': 'name', 'pass': 'password'}) == {'name': 'name'}
        assert Password.definitions() == {
            'properties': {
                'name': {'type': 'string'},
                'pass': {'format': 'password', 'type': 'string', 'load_only': 'true'}
            },
            'type': 'object'
        }

    def test_schema_raise_error_if_schema_already_exists(self):
        class NewSchema(Schema):
            type = 'object'
            properties = {
                'name': {
                    'type': 'string',
                },
                'pass': {
                    'type': 'string',
                    'format': 'password',
                    'load_only': 'true'
                }
            }
        with pytest.raises(SchemaAlreadyExist) as e:
            class NewSchema(Schema):
                pass

        assert str(e.value.message) == "You must not create 2 or more schemas with the same name:" \
                                       " NewSchema already exists"

    def test_schema_raise_error_when_properties_is_not_dict(self):
        with pytest.raises(TypeError):
            class BadPropertiesSchema(Schema):
                type = 'object'
                properties = 'name'

    def test_schema_raise_error_when_properties_is_null_and_type_is_object(self):
        with pytest.raises(TypeError):
            class MissingPropertiesSchema(Schema):
                type = 'object'

    def test_schema_raise_error_when_item_is_load_only_and_dump_only(self):
        class SchemaDumpOnlyAndLoadOnly(Schema):
            type = 'object'
            properties = {
                'name': {
                    'type': 'string',
                    'load_only': 'true',
                    'dump_only': 'true'
                }
            }

        with pytest.raises(TypeError):
            SchemaDumpOnlyAndLoadOnly(**{'name': 'test'})

        class SchemaTypeDumpOnlyAndLoadOnly(Schema):
            type = 'string'
            load_only = 'true'
            dump_only = 'true'

        class SecondSchemaDumpOnlyAndLoadOnly(Schema):
            type = 'object'
            properties = {
                'name': SchemaTypeDumpOnlyAndLoadOnly
            }

        with pytest.raises(TypeError):
            SecondSchemaDumpOnlyAndLoadOnly(**{'name': 'test'})

    def test_schema_valid_when_load_only(self, user_model):
        user = {
            'id': 1,
            'name': 'test',
            'password': 'password'
        }
        user_result = {
            'id': 1,
            'name': 'test'
        }
        assert user_model(**user) == user_result

    def test_schema_valid_when_load_only_and_null(self, user_model):
        user = {
            'id': 1,
            'name': 'test',
            'password': None
        }
        user_result = {
            'id': 1,
            'name': 'test'
        }
        assert user_model(**user) == user_result

    def test_schema_valid_when_load_only_and_true(self):
        class SchemaLoadOnlyAndTrue(Schema):
            type = 'object'
            properties = {
                'id': {
                    'type': 'int'
                },
                'name': {
                    'type': 'string',
                },
                'value': {
                    'type': 'boolean',
                    'load_only': 'true'
                }
            }

        user = {
            'id': 1,
            'name': 'test',
            'value': True
        }

        user_result = {
            'id': 1,
            'name': 'test',
        }
        assert SchemaLoadOnlyAndTrue(**user) == user_result

    def test_schema_valid_when_load_only_and_false(self):
        class SchemaLoadOnlyAndFalse(Schema):
            type = 'object'
            properties = {
                'id': {
                    'type': 'int'
                },
                'name': {
                    'type': 'string',
                },
                'value': {
                    'type': 'boolean',
                    'load_only': 'true'
                }
            }

        user = {
            'id': 1,
            'name': 'test',
            'value': False
        }

        user_result = {
            'id': 1,
            'name': 'test',
        }
        assert SchemaLoadOnlyAndFalse(**user) == user_result
