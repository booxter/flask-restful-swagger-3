import pytest

from flask_restful_swagger_3.swagger_format import ValidateFormat, get_validate_format


class TestSwaggerFormat:
    def test_create_format_validator_class_ok(self):
        class NewValidator(ValidateFormat):
            def validate(self):
                pass
        assert NewValidator()

    def test_create_format_validator_class_raise_error_when_missing_validate_method(self):
        class NewValidator(ValidateFormat):
            pass

        with pytest.raises(NotImplementedError):
            NewValidator().validate()

    def test_get_existing_validator_ok(self):
        assert get_validate_format('string', 'email')

    def test_get_non_existing_validator_return_none(self):
        assert not get_validate_format('string', 'non_exist')

    def test_validate_format_int_32(self):
        get_validate_format('integer', 'int32')().validate(5)

    def test_validate_format_int_32_raises_error_when_value_is_out_of_edge(self):
        with pytest.raises(ValueError):
            get_validate_format('integer', 'int32')().validate(44444444444444444444444444444444)

    def test_validate_format_int_64(self):
        get_validate_format('integer', 'int64')().validate(5)

    def test_validate_format_int_64_raises_error_when_value_is_out_of_edge(self):
        with pytest.raises(ValueError):
            get_validate_format('integer', 'int64')().validate(44444444444444444444444444444444)

    def test_validate_format_email(self):
        get_validate_format('string', 'email')().validate('email@fake.fr')

    def test_validate_format_format_raises_error_when_value_is_not_email(self):
        with pytest.raises(ValueError):
            get_validate_format('string', 'email')().validate('fake')
