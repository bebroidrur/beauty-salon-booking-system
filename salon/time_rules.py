"""Canonical conversion of instants to salon time."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

KYIV = ZoneInfo('Europe/Kyiv')
DAYS = ('monday','tuesday','wednesday','thursday','friday','saturday','sunday')


def instant(value):
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def local(value):
    return value.astimezone(KYIV).isoformat()

