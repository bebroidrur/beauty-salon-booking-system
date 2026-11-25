"""Validation against the unchanged, checked-in OpenAPI contract."""

from pathlib import Path

import yaml
from jsonschema import validators
from openapi_schema_validator import OAS30Validator

from salon.numeric_validation import exact_multiple

API = yaml.safe_load(
    (Path(__file__).resolve().parents[1] / "spec/openapi.yaml").read_text()
)


def resolve(value):
    """Return a recursively expanded copy of an OpenAPI schema value.

    Args:
        value: Dictionary, list or scalar from the checked-in contract.

    Returns:
        Value with local references expanded through the module-level API mapping.

    Raises:
        KeyError: If a referenced path does not exist.

    Notes:
        Intended for this contract's acyclic local references; external references
        and cycles are not supported.
    """
    if isinstance(value, dict):
        if "$ref" in value:
            result = API
            for part in value["$ref"][2:].split("/"):
                result = result[part]
            return resolve(result)
        return {k: resolve(v) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(v) for v in value]
    return value


ContractValidator = validators.extend(
    OAS30Validator, {"multipleOf": exact_multiple}
)


def validate(schema, value):
    """Validate a JSON value using the resolved OpenAPI 3.0 schema.

    Args:
        schema: Contract schema, possibly containing local references.
        value: Decoded JSON value to check.

    Raises:
        ValidationError: If value violates the schema or a checked format.

    Notes:
        Returns None on success. Decimal multipleOf uses exact rational arithmetic.
    """
    ContractValidator(
        resolve(schema), format_checker=OAS30Validator.FORMAT_CHECKER
    ).validate(value)
