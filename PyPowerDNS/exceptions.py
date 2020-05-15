class PDNSApiException(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        super(PDNSApiException, self).__init__()

    def __str__(self):
        return f"status_code={self.status}: {self.message})"

    def __repr__(self):
        return f"{type(self).__name__}({self.status}: {self.message})"


class PDNSApiNotFound(Exception):
    pass
