import json
import os

import jsonschema
from jsonschema import validate


def getJsonSchema(fileToLoad): # Loads the JSON schema file
    cd = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
    with open(cd + '/Schemas/JSON/' + fileToLoad + '.json', 'r') as file:
        schema = json.load(file)
        if schema is None:
            print("Could not load JSON schema")
            return False
    return schema


def validateJson(jsonData, jsonSchema): # Validates the JSON data against the JSON schema
    execute_api_schema = getJsonSchema(jsonSchema)
    if execute_api_schema is False:
        print("JSON schema not found")
        return False

    try:
        validate(instance=jsonData, schema=execute_api_schema)
    except jsonschema.exceptions.ValidationError as err:
        print("JSON Scheme Validation error" + str(err))
        return False
    except jsonschema.exceptions.SchemaError as err:
        print("JSON Scheme Schema error" + str(err))
        return False
    return True
