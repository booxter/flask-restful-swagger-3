import pytest
from tests.fixtures.fixture_models import SchemaTestModel


class TestSchema:
    def test_should_validate_schema_valid(self):
        assert SchemaTestModel(**{'id': 1, 'name': 'somebody'}) == {'id': 1, 'name': 'somebody'}

    def test_should_validate_schema_missing_required(self):
        with pytest.raises(ValueError):
            SchemaTestModel(**{'name': 'somebody'})

    def test_should_validate_schema_invalid_type(self):
        with pytest.raises(ValueError):
            SchemaTestModel(**{'id': '1'})