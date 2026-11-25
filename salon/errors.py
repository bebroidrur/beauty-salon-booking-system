"""Define structured errors translated by the HTTP adapter."""


class ApiError(Exception):
    """Carry an HTTP status, stable API code and client-facing message.

    The adapter serializes code and message; exception text contains only code.
    """

    def __init__(self, status, code, message):
        """Store status (HTTP integer), code and message (strings)."""
        self.status, self.code, self.message = status, code, message
        super().__init__(code)


def reject(
    status,
    code="VALIDATION_ERROR",
    message="Дані не відповідають схемі або правилам.",
):
    """Raise a structured API error without changing persistent state.

    Args:
        status: HTTP response status integer.
        code: Stable error code; defaults to VALIDATION_ERROR.
        message: Client-facing text that must not contain secrets.

    Raises:
        ApiError: Always, carrying the supplied fields.
    """
    raise ApiError(status, code, message)
