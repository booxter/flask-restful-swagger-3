class SchemaAlreadyExist(Exception):
    def __init__(self, schema_name):
        self.schema_name = schema_name

    @property
    def message(self):
        return f"You must not create 2 or more schemas with the same name: {self.schema_name} already exists"
