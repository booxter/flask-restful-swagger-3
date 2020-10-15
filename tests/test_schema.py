import pytest
from tests.fixtures.fixture_models import SchemaTestModel, NestedSchema


class TestSchema:
    def test_should_validate_schema_valid(self):
        assert SchemaTestModel(**{'id': 1, 'name': 'somebody'}) == {'id': 1, 'name': 'somebody'}

    def test_should_validate_schema_missing_required(self):
        with pytest.raises(ValueError):
            SchemaTestModel(**{'name': 'somebody'})

    def test_should_validate_schema_invalid_type(self):
        with pytest.raises(ValueError):
            SchemaTestModel(**{'id': '1'})

    def test_should_validate_nested_schema_ok(self, nested_obj):
        NestedSchema(**nested_obj)

    def test_should_no_validate_nested_schema_invalid_type(self, bad_type_in_nested_obj):
        with pytest.raises(ValueError):
            NestedSchema(**bad_type_in_nested_obj)