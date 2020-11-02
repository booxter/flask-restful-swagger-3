def operation_object():
    return {
        'tags': ['user'],
        'description': 'Returns a user',
        'deprecated': True,
        'responses': {
            '200': {
                'description': 'Get users',
                'content': {
                    'application/json': {
                        'schema': {
                            "$ref": "#/components/schemas/UserModel"
                        },
                        'example': {
                            'application/json': {
                                'id': 1,
                                'name': 'somebody'
                            }
                        }
                    }
                }
            }
        },
        'requestBody': {
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/User"
                    },
                    "examples": {
                        "user": {
                            "summary": "User Example",
                            "externalValue": "http://foo.bar/examples/user-example.json"
                        }
                    }
                }
            }
        },
        'externalDocs': {
            "url": "https://example.com"
        },
        'security': {
            "api_key": []
        }
    }


def parameter_object():
    return {
        'name': 'name',
        'in': 'query',
        'description': 'something',
        'required': False,
        'deprecated': False,
        'allowEmptyValue': False,
        'style': '',
        'explode': '',
        'allowReserved': 'test',
        'schema': {'type': 'string'},
    }


def responses_object():
    return {
        "4XX": {
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorSchema"
                    },
                    "example": {
                        "message": "string"
                    }
                }
            },
            "description": "Bad request"
        },
        "200": {
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/CategoryDumpSchema"
                    },
                    "example": [
                        {
                            "parents": [
                                {
                                    "name": "string",
                                    "products": [
                                        {
                                            "category_id": "string",
                                            "global_category": "string",
                                            "id": "string",
                                            "name": "string",
                                            "picture": "string",
                                            "unit_price": "number",
                                            "unit": "string",
                                            "quantity": "number"
                                        }
                                    ],
                                    "id": "string"
                                }
                            ],
                            "children": [
                                {
                                    "name": "string",
                                    "products": [
                                        {
                                            "category_id": "string",
                                            "global_category": "string",
                                            "id": "string",
                                            "name": "string",
                                            "picture": "string",
                                            "unit_price": "number",
                                            "unit": "string",
                                            "quantity": "number"
                                        }
                                    ],
                                    "id": "string"
                                }
                            ],
                            "id": "string",
                            "name": "string",
                            "products": [
                                {
                                    "category_id": "string",
                                    "global_category": "string",
                                    "id": "string",
                                    "name": "string",
                                    "picture": "string",
                                    "unit_price": "number",
                                    "unit": "string",
                                    "quantity": "number"
                                }
                            ]
                        }
                    ]
                }
            },
            "description": "List category"
        }
    }


def request_body():
    return {
               "content": {
                   "application/json": {
                       "schema": {
                            "$ref": "#/components/schemas/CategoryCreationSchema"
                       }
                   }
               },
               "description": "Request body",
               "required": True
    }


def components_schemas_object():
    return {
        "schemas": {
            "HelloSchema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string"
                    },
                    "message": {
                        "type": "string"
                    }
                }
            },
            'RefSchema': {
                "$ref": "#/components/schemas/CategoryCreationSchema"
            },
            'SecondRefSchema': {
                "$ref": "#/components/schemas/CategoryCreationSchema"
            },
            'RequiredSchema': {
                'required': ['something']
            }
        }
    }


def components_responses_object():
    return {
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/CategoryDumpSchema"
                        },
                        "example": [
                            {
                                "parents": [
                                    {
                                        "name": "string",
                                        "products": [
                                            {
                                                "category_id": "string",
                                                "global_category": "string",
                                                "id": "string",
                                                "name": "string",
                                                "picture": "string",
                                                "unit_price": "number",
                                                "unit": "string",
                                                "quantity": "number"
                                            }
                                        ],
                                        "id": "string"
                                    }
                                ],
                                "children": [
                                    {
                                        "name": "string",
                                        "products": [
                                            {
                                                "category_id": "string",
                                                "global_category": "string",
                                                "id": "string",
                                                "name": "string",
                                                "picture": "string",
                                                "unit_price": "number",
                                                "unit": "string",
                                                "quantity": "number"
                                            }
                                        ],
                                        "id": "string"
                                    }
                                ],
                                "id": "string",
                                "name": "string",
                                "products": [
                                    {
                                        "category_id": "string",
                                        "global_category": "string",
                                        "id": "string",
                                        "name": "string",
                                        "picture": "string",
                                        "unit_price": "number",
                                        "unit": "string",
                                        "quantity": "number"
                                    }
                                ]
                            }
                        ]
                    }
                },
                "description": "List category"
            }
        }
    }


def components_parameters_object():
    return {
        "parameters": {
            'CategoryId': {
                "description": "category_id",
                "in": "path",
                "name": "category_id",
                "required": "true"
            },
            'RefCategory': {
                "$ref": "#/components/parameters/CategoryId"
            }
        }
    }


def components_examples_object():
    return {
        "examples": {
            'CategoryExample': {
                'summary': 'short example',
                'description': 'long example',
                'value': {
                    'name': 'test',
                    'id': 1
                },
                'externalValue': 'external url or yaml or json'
            },
            'RefCategoryExample': {
                "$ref": "#/components/examples/CategoryExample"
            }
        }
    }


def components_request_bodies_object():
    return {
        "requestBodies": {
            'CategoryRequestBody': {
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/CategoryCreationSchema"
                        }
                    }
                },
                "description": "Request body",
                "required": True
            },
            'RefCategoryRequestBody': {
                "$ref": "#/components/requestBodies/CategoryRequestBody"
            }
        }
    }


def components_headers_object():
    return {
        "headers": {
            'X-Something-Bidule': {
                "description": "Location of the new item",
                "schema": {
                    "type": "string"
                }
            },
            'X-Other-Something': {
                '$ref': "#/components/headers/X-Something-Bidule"
            }
        }
    }


def components_security_schemes_object():
    return {
        "securitySchemes": {
            'auth': {
                "type": "oauth2",
                "flows": {
                    "implicit": {
                        "authorizationUrl": "https://example.com/api/oauth/dialog",
                        "scopes": {
                            "write:pets": "modify pets in your account",
                            "read:pets": "read your pets"
                        }
                    }
                }
            },
            'auth-password': {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "authorizationUrl": "https://example.com/api/oauth/dialog",
                        "scopes": {
                            "write:pets": "modify pets in your account",
                            "read:pets": "read your pets"
                        },
                        'tokenUrl': "https://example.com/api/oauth/dialog"
                    }
                }
            },
            'auth-clientCredentials': {
                "type": "oauth2",
                "flows": {
                    "clientCredentials": {
                        "authorizationUrl": "https://example.com/api/oauth/dialog",
                        "scopes": {
                            "write:pets": "modify pets in your account",
                            "read:pets": "read your pets"
                        },
                        'tokenUrl': "https://example.com/api/oauth/dialog"
                    }
                }
            },
            'auth-authorizationCode': {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "https://example.com/api/oauth/dialog",
                        "scopes": {
                            "write:pets": "modify pets in your account",
                            "read:pets": "read your pets"
                        },
                        'tokenUrl': "https://example.com/api/oauth/dialog",
                        'refreshUrl': "https://example.com/api/oauth/dialog"
                    }
                }
            },
            'api-key': {
                "type": "apiKey",
                "name": "api_key",
                "in": "header"
            },
            'http': {
                "type": "http",
                "scheme": "basic"
            },
            'http-bearer': {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            },
            'openId': {
                "type": "openIdConnect",
                "openIdConnectUrl": "https://open-id-connect-url.fr"
            },
            'ref_auth': {
                '$ref': "#/components/securitySchemes/auth"
            }
        }
    }


def components_link_object():
    return {
        'links': {
            'UserRepositories': {
                'operationRef': '#/paths/~12.0~1repositories~1{username}/get',
                'parameters': {
                    'username': '$response.body#/username'
                },
                'description': 'some description',
                'server': {
                    "url": "https://development.gigantic-server.com/v1",
                    "description": "Development server",
                    "variables": {
                        "enum": ['string', 'test', 'something'],
                        "default": "test",
                        "description": "the server"
                    }
                }
            },
            'RefUserRepositories': {
                '$ref': "#/components/links/UserRepositories"
            }
        }
    }


def components_callback_object():
    return {
        'callbacks': {
            'myFirstCallback': {
                "servers": {
                    "url": "https://development.gigantic-server.com/v1",
                },
                "post": {
                    "tags": [
                        "users"
                    ],
                    "responses": {
                        "201": {
                            "description": "Created user",
                            "headers": {
                                'X-Something-Bidule': {
                                    "description": "Location of the new item",
                                    "schema": {
                                        "type": "string"
                                    }
                                }
                            },
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/UserModel"
                                    },
                                    "example": {
                                        "application/json": {
                                            "id": 1
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                '$ref': "",
                "parameters": [
                    {
                        "name": "body",
                        "description": "Request body",
                        "in": "query",
                        "schema": {
                            "$ref": "#/components/schemas/UserModel"
                        },
                        "required": True
                    }
                ],
                'summary': "Add a user",
                "description": "Adds a user",
            },
            'myFirstCallbackRef': {
                '$ref': "#/components/callbacks/myFirstCallback"
            }
        }
    }


def server_object():
    return {
            "url": "https://development.gigantic-server.com/v1",
            "description": "Development server",
            "variables": {
                "enum": ['string', 'test', 'something'],
                "default": "test",
                "description": "the server"
            }
    }
