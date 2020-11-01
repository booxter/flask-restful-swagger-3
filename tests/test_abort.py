import pytest
from flask_restful_swagger_3 import abort


class TestAbort:
    def test_abort(self):
        with pytest.raises(Exception):
            abort(500)

    def test_abort_with_args(self):
        with pytest.raises(Exception) as e:
            abort(500, schema={"message": "I have an internal server error"})

        assert "message" in e.value.data
        assert e.value.data["message"] == "I have an internal server error"

    def test_abort_with_kwargs(self):
        with pytest.raises(Exception) as e:
            abort(500, key_error="I have an internal server error")

        assert "key_error" in e.value.data
        assert e.value.data["key_error"] == "I have an internal server error"
