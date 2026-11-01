"""Decimal JSON-schema arithmetic without binary floating-point remainders."""
from fractions import Fraction
from jsonschema.exceptions import ValidationError


def exact_multiple(validator, divisor, instance, schema):
    if not validator.is_type(instance, 'number'):
        return
    try:
        valid = (Fraction(str(instance)) / Fraction(str(divisor))).denominator == 1
    except (ValueError, ZeroDivisionError):
        valid = False
    if not valid:
        yield ValidationError('Number is not an exact decimal multiple')

