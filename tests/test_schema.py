import pytest


class TestSchema:
    def test_should_validate_schema_valid(self, schema_test_model):
        assert schema_test_model(**{'id': 1, 'name': 'somebody'}) == {'id': 1, 'name': 'somebody'}

    def test_should_validate_schema_missing_required(self, schema_test_model):
        with pytest.raises(ValueError):
            schema_test_model(**{'name': 'somebody'})

    def test_should_validate_schema_invalid_type(self, schema_test_model):
        with pytest.raises(ValueError):
            schema_test_model(**{'id': '1'})

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
        sub_schema(**obj_of_sub_schema)

    def test_should_raise_error_when_validate_obj_with_sub_schema_different_type(
            self, bad_sub_schema, obj_of_sub_schema):
        with pytest.raises(TypeError):
            bad_sub_schema(**obj_of_sub_schema)

    def test_should_raise_error_when_validate_obj_with_sub_schema_with_bad_super_schema(
            self, sub_schema_with_bad_super_schema, obj_of_sub_schema):
        with pytest.raises(TypeError):
            sub_schema_with_bad_super_schema(**obj_of_sub_schema)
