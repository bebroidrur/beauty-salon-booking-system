def create_booking(client_name, service, master, time):
    return {
        "client": client_name,
        "service": service,
        "master": master,
        "time": time
    }