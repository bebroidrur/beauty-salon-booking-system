"""Allowlisted diagnostic events: never serialize request or exception objects."""

import json
import logging
from datetime import datetime, timezone


def record(operation, status, request_id, code=None):
    """Emit one allowlisted JSON diagnostic event at INFO level.

    Args:
        operation: Safe operation name, never a URL or request body.
        status: Numeric HTTP-style result status.
        request_id: Correlation identifier for the request or mail job.
        code: Optional safe error code; defaults to None.

    Notes:
        Returns None. Callers supply safe values; this function does not redact
        arbitrary strings and must not receive secrets or personal data.
    """
    logging.getLogger("salon.events").info(
        json.dumps(
            dict(
                time=datetime.now(timezone.utc).isoformat(),
                requestId=request_id,
                operation=operation,
                status=status,
                code=code,
            )
        )
    )
