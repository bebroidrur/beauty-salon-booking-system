"""Decimal JSON-schema arithmetic without binary floating-point remainders."""

from fractions import Fraction

from jsonschema.exceptions import ValidationError


def exact_multiple(validator, divisor, instance, schema):
    """Yield a validation error when a number is not an exact decimal multiple.

    Args:
        validator: JSON Schema validator exposing is_type.
        divisor: multipleOf schema value, converted through its string form.
        instance: JSON value; nonnumeric values are ignored by this keyword.
        schema: Enclosing schema, accepted for the validator callback interface.

    Yields:
        ValidationError: If the ratio is nonintegral or cannot be calculated.
    """
    if not validator.is_type(instance, "number"):
        return
    try:
        valid = (
            Fraction(str(instance)) / Fraction(str(divisor))
        ).denominator == 1
    except (ValueError, ZeroDivisionError):
        valid = False
    if not valid:
        yield ValidationError("Number is not an exact decimal multiple")
