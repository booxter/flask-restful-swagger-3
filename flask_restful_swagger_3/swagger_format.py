import re


class ValidateFormat:
    def validate(self):
        raise NotImplementedError()


class Int32:
    max_value = 2147483647
    min_value = -2147483648

    def validate(self, value):
        if not self.min_value <= value <= self.max_value:
            raise ValueError(f"Value {value} must be between {self.min_value} and {self.max_value}")


class Int64:
    max_value = 9223372036854775807
    min_value = -9223372036854775808

    def validate(self, value):
        if not self.min_value <= value <= self.max_value:
            raise ValueError(f"Value {value} must be between {self.min_value} and {self.max_value}")


class Email:
    regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'  # quoted-string
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)

    def validate(self, value):
        if not re.match(self.regex, value) is not None:
            raise ValueError(f"Value {value} must be an email")


def get_validate_format(type_, format_):
    format_dict = {
        'string': {
            'email': Email,
        },
        'integer': {
            'int32': Int32,
            'int64': Int64
        }
    }

    if type_ in format_dict:
        return format_dict[type_].get(format_, None)
