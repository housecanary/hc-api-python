"""
This module provides a base class and two implementations of OutputGenerator,
which is responsible for processing a response before returning a result to the caller.

An OutputGenerator must implement a `process_response` method
which takes an input (usually a server's response to an HTTP request)
and returns something useful to the caller. This is a good place to do
custom serialization of an API response.
"""

try:
    # Python 3
    from urllib.parse import urlparse
except ImportError:
    # Python 2
    from urlparse import urlparse

from housecanary.response import Response
import housecanary.exceptions
import housecanary.constants as constants


class OutputGenerator(object):
    """Base class of an OutputGenerator. This base class just returns the given response."""

    def process_response(self, response):
        """Simply returns the response passed in."""
        return response


class JsonOutputGenerator(OutputGenerator):
    """Returns the JSON body of the response

    Expects the given response to implement a `json` method,
    like the response from the requests library.
    """

    def process_response(self, response):
        """Return the result of calling the json method on response"""
        return response.json()


class ResponseOutputGenerator(OutputGenerator):
    """Serializes the response into an instance of Response.

    Expects the given response to be a response from the requests library.
    """

    def process_response(self, response):
        content_type = response.headers['content-type']

        if content_type == "application/json":
            return self.process_json_response(response)
        elif content_type == "application/pdf":
            return self.process_pdf_response(response)
        elif content_type == "appliction/zip":
            return self.process_zip_response(response)
        else:
            return response

    def process_json_response(self, response):
        """For a json response, check if there was any error and throw exception.
        Otherwise, create a housecanary.response.Response."""

        response_json = response.json()

        # handle errors
        code_key = "code"
        if code_key in response_json and response_json[code_key] != constants.HTTP_CODE_OK:
            code = response_json[code_key]

            message = response_json
            if "message" in response_json:
                message = response_json["message"]
            elif "code_description" in response_json:
                message = response_json["code_description"]

            if code == constants.HTTP_FORBIDDEN:
                raise housecanary.exceptions.UnauthorizedException(code, message)
            else:
                raise housecanary.exceptions.RequestException(code, message)

        request_url = response.request.url

        endpoint_name = self._parse_endpoint_name_from_url(request_url)

        return Response.create(endpoint_name, response_json, response)

    def process_pdf_response(self, response):
        return response.text

    def process_zip_response(self, response):
        return response.text

    @staticmethod
    def _parse_endpoint_name_from_url(request_url):
        # get the path from the url
        path = urlparse(request_url).path

        # path is like "/v2/property/value"

        # strip off the leading "/"
        path = path[1:]

        # keep only the part after the version and "/"
        path = path[path.find("/")+1:]

        # path is now like "property/value"
        return path
