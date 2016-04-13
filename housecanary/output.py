"""
housecanary.output

This module provides a base class and two implementations of OutputGenerator,
which is responsible for processing a response from the HouseCanary API
before returning a result to the caller.

An OutputGenerator must implement a `process_response` method
which takes an input (usually a server's response to an HTTP request)
and returns something useful to the caller. This is a good place to do
custom serialization of an API response.

"""

import json

try:
    # Python 3
    from urllib.parse import urlparse
except ImportError:
    # Python 2
    from urlparse import urlparse

from housecanary.hcresponse import HouseCanaryResponse
import housecanary.exceptions

HTTP_CODE_OK = 200
HTTP_FORBIDDEN = 403

class OutputGenerator(object):
    """Base class of an OutputGenerator. This base class just returns the given response."""

    def process_response(self, response):
        return response

class JsonOutputGenerator(OutputGenerator):
    """An implementation of OutputGenerator that simply returns the JSON body of the response

    Expects the given response to implement a `json` method,
    like the response from the requests library.
    """

    def process_response(self, response):
        return response.json()

class HCResponseOutputGenerator(OutputGenerator):
    """An implementation of OutputGenerator that serializes the response
    into an instance of HouseCanaryResponse.

    Expects the given response to be a response from the requests library.
    """

    def process_response(self, response):
        response_json = response.json()

        # handle errors
        code_key = "code"
        if code_key in response_json and response_json[code_key] != HTTP_CODE_OK:
            code = response_json[code_key]

            if "message" in response_json:
                message = response_json["message"]

            if code == HTTP_FORBIDDEN:
                raise housecanary.exceptions.UnauthorizedException(code, message)
            else:
                raise housecanary.exceptions.RequestException(code, message)

        request_url = response.request.url

        endpoint_name = self._parse_endpoint_name_from_url(request_url)

        return HouseCanaryResponse(endpoint_name, response_json, response)

    @staticmethod
    def _parse_endpoint_name_from_url(request_url):
        # get the path from the url
        path = urlparse(request_url).path

        # path is like "/v2/property/score"

        # strip off the leading "/"
        path = path[1:]

        # keep only the part after the version and "/"
        path = path[path.find("/")+1:]

        # path is now like "property/score"
        return path