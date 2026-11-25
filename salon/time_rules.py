"""Canonical conversion of instants to salon time."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

KYIV = ZoneInfo("Europe/Kyiv")
DAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)


def instant(value):
    """Parse an ISO datetime string value and return an aware UTC datetime.

    Raises:
        ValueError: If value is not a parseable ISO datetime string.

    Notes:
        API callers must supply an explicit offset as required by the contract.
        A naive value follows Python's host-local timezone conversion behavior.
    """
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def local(value):
    """Return aware datetime value as an ISO string in Europe/Kyiv.

    Naive inputs follow the host-local timezone; API callers supply aware values.
    """
    return value.astimezone(KYIV).isoformat()
