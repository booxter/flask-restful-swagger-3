import pytest
from flask_restful.reqparse import RequestParser

from flask_restful_swagger_3 import RequestParserExtractor, swagger


class TestRequestParserExtractor:
    def test_no_reqparser(self):
        assert RequestParserExtractor(None).extract() == []

    def test_name_not_in_reqparser(self):
        with pytest.raises(swagger.ValidationError) as e:
            RequestParserExtractor({"parser": ""}).extract()

        assert str(e.value) == "name must be define in reqparser"

    def test_parser_not_in_reqparser(self):
        with pytest.raises(swagger.ValidationError) as e:
            RequestParserExtractor({"name": "test"}).extract()

        assert str(e.value) == "parser must be define in reqparser"

    def test_parser_params(self):
        def boolean():
            return True

        class Default(str):
            swagger_default = 'default'

        post_parser = RequestParser()
        post_parser.add_argument('id', type=int, help='id help', location='args')
        post_parser.add_argument('User-Agent', type=str, location='headers')
        post_parser.add_argument('post', type=boolean, location='view_args')
        post_parser.add_argument('other', type=bin, location='other')
        post_parser.add_argument('my_list', type=list, location='args')
        post_parser.add_argument('my_obj', type=dict, location='args', required=True)
        post_parser.add_argument('another_list', type=str, location='args', required=True, action='append')
        post_parser.add_argument('default', type=Default, location='args', default=Default)

        parser_json_result, params = RequestParserExtractor({'name': "id", "parser": post_parser}).extract()
        assert parser_json_result == {}
        assert params == [
            {
                'name': 'id', 'description': 'id help', 'required': False, 'type': 'integer', 'in': 'query'
            },
            {
                'name': 'User-Agent', 'description': None, 'required': False, 'type': 'string', 'in': 'header'
            },
            {
                'name': 'post', 'description': None, 'required': False, 'type': 'boolean', 'in': 'path'
            },
            {
                'name': 'other', 'description': None, 'required': False, 'type': 'binary', 'in': 'other'
            },
            {
                'name': 'my_list', 'description': None, 'required': False, 'type': 'array', 'in': 'query'
            },
            {
                'name': 'my_obj', 'description': None, 'required': True, 'type': 'object', 'in': 'query'
            },
            {
                'name': 'another_list', 'description': None, 'required': True,
                'items': {'type': 'string'}, 'type': 'array', 'in': 'query'
            },
            {
                'name': 'default', 'description': None, 'required': False,
                'default': 'default', 'type': 'string', 'in': 'query'
            }
        ]

    def test_parser_unexpected_type(self):
        post_parser = RequestParser()
        post_parser.add_argument('no_type', type='something', location='args', required=True)
        with pytest.raises(TypeError) as e:
            RequestParserExtractor({'name': "id", "parser": post_parser}).extract()

        assert str(e.value) == "unexpected type: something"
