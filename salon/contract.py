"""Validation against the unchanged, checked-in OpenAPI contract."""
from pathlib import Path
from fractions import Fraction
from jsonschema import validators
from jsonschema.exceptions import ValidationError
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


def exact_multiple(validator, divisor, instance, schema):
    if not validator.is_type(instance, 'number'):
        return
    try:
        valid = (Fraction(str(instance)) / Fraction(str(divisor))).denominator == 1
    except (ValueError, ZeroDivisionError):
        valid = False
    if not valid:
        yield ValidationError('Number is not an exact decimal multiple')


ContractValidator = validators.extend(OAS30Validator, {'multipleOf': exact_multiple})


def validate(schema, value):
    ContractValidator(resolve(schema), format_checker=OAS30Validator.FORMAT_CHECKER).validate(value)
