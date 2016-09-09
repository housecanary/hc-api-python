from . import utilities

class RequestException(Exception):
    """Exception representing an error due to an incorrect request structure
    or missing required fields."""

    def __init__(self, status_code, message):
        Exception.__init__(self)
        self._status_code = status_code
        self._message = message

    def __str__(self):
        return "%s (HTTP Status: %s)" % (self._message, self._status_code)


class RateLimitException(RequestException):
    """Exception for 429 rate limit exceeded"""

    def __init__(self, status_code, message, response):
        RequestException.__init__(self, status_code, message)
        self._response = response
        self._rate_limits = None

    def __str__(self):
        return "%s (HTTP Status: %s) (Resets at: %s)" % (
            self._message, self._status_code, self._get_rate_limit_reset())

    @property
    def rate_limits(self):
        """Returns list of rate limit information from the response"""
        if not self._rate_limits:
            self._rate_limits = utilities.get_rate_limits(self._response)
        return self._rate_limits

    def _get_rate_limit_reset(self):
        return self.rate_limits[0]["reset"]


class UnauthorizedException(RequestException):
    """Exception for unauthenticated or unauthorized request."""
    pass


class InvalidInputException(Exception):
    """Exception representing invalid input passed to the API Client."""
    pass
