def fixture_nested_obj():
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


def fixture_bad_type_in_nested_obj():
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


def fixture_enum_obj():
    return {
        'my_choice': 'choice_1'
    }


def fixture_enum_obj_not_in_choice():
    return {
        'my_choice': 'not_in_choice'
    }