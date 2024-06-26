def nested_obj():
    return {
        'id': 1,
        'name': 'fake',
        'category': {
            'id': 1,
            'name': 'fake category',
            'property': {
                'property1': 'fake',
                'property2': 'fake'
            }
        },
        'mail': 'tes@test.fr'
    }


def bad_type_in_nested_obj():
    return {
        'id': 1,
        'name': 'fake',
        'category': {
            'id': 1,
            'name': 'fake category',
            'property': {
                'property1': 2,
                'property2': 'fake'
            }
        }
    }


def enum_obj():
    return {
        'my_choice': 'choice_1'
    }


def enum_obj_not_in_choice():
    return {
        'my_choice': 'not_in_choice'
    }


def obj_of_sub_schema():
    return {
        'id': 'my_id',
        'super_attribute': 'super',
        'other_attribute': 'other',
        'sub_attribute': 'sub'
    }


def expected_definition_of_sub_schema():
    return {
        'properties': {
            'sub_attribute': {'type': 'string'},
            'id': {'type': 'string'},
            'super_attribute': {'type': 'string'},
            'other_attribute': {'type': 'string'}
        },
        'required': ['sub_attribute', 'other_attribute']
    }


def expected_example_of_sub_schema():
    return {
        'sub_attribute': 'string',
        'id': 'string',
        'super_attribute': 'string',
        'other_attribute': 'string'
    }


def object_with_array():
    return {
        "id": 1,
        "name": "test",
        "my_test_array": [
            {
                "id": 1,
                "prop1": "test",
                "prop2": "test"
            }
        ]
    }
