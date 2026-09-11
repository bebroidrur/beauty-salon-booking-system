CANCELLATION_HOURS_BEFORE = 2


def can_cancel_booking(hours_before):
    return hours_before >= CANCELLATION_HOURS_BEFORE


def create_booking(client_name, service, master, time):
    return {
        "client": client_name,
        "service": service,
        "master": master,
        "time": time
    }
