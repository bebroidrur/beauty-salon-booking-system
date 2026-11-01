class ApiError(Exception):
    def __init__(self, status, code, message):
        self.status, self.code, self.message = status, code, message
        super().__init__(code)


def reject(status, code='VALIDATION_ERROR', message='Дані не відповідають схемі або правилам.'):
    raise ApiError(status, code, message)
