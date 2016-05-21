class RequestException(Exception):
    """Exception representing an error due to an incorrect request structure
    or missing required fields."""

    def __init__(self, status_code, message):
        Exception.__init__(self)
        self._status_code = status_code
        self._message = message

    def __str__(self):
        return "%s (HTTP Status: %s)" % (self._message, self._status_code)


class UnauthorizedException(RequestException):
    """Exception for unauthenticated or unauthorized request."""
    pass


class InvalidInputException(Exception):
    """Exception representing invalid input passed to the API Client."""
    pass
