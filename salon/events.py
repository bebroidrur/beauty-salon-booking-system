"""Allowlisted diagnostic events: never serialize request or exception objects."""
from datetime import datetime,timezone
import json
import logging


def record(operation, status, request_id, code=None):
    logging.getLogger('salon.events').info(json.dumps(dict(
        time=datetime.now(timezone.utc).isoformat(), requestId=request_id,
        operation=operation, status=status, code=code)))
