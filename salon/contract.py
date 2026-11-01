"""Validation against the unchanged, checked-in OpenAPI contract."""
from pathlib import Path
from jsonschema import validators
from salon.numeric_validation import exact_multiple
import yaml
from openapi_schema_validator import OAS30Validator

API = yaml.safe_load((Path(__file__).resolve().parents[1] / 'spec/openapi.yaml').read_text())


def resolve(value):
    if isinstance(value, dict):
        if '$ref' in value:
            result = API
            for part in value['$ref'][2:].split('/'):
                result = result[part]
            return resolve(result)
        return {k: resolve(v) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(v) for v in value]
    return value




ContractValidator = validators.extend(OAS30Validator, {'multipleOf': exact_multiple})


def validate(schema, value):
    ContractValidator(resolve(schema), format_checker=OAS30Validator.FORMAT_CHECKER).validate(value)
