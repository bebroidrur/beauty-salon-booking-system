"""Preserve the historical booking sketch; the salon backend does not use it."""


def create_booking(client_name, service, master, time):
    """Return the historical four-field booking dictionary without validation.

    Args:
        client_name: Value stored under client, not a registered client ID.
        service: Value stored under service, not a service snapshot.
        master: Value stored under master.
        time: Value stored under time, without timezone conversion.

    Returns:
        Dictionary with the original client, service, master and time values.

    Notes:
        This sketch neither persists nor implements the production API contract.
    """
    return {
        "client": client_name,
        "service": service,
        "master": master,
        "time": time,
    }
