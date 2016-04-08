import uuid
import json
from housecanary.housecanaryproperty import HouseCanaryProperty

class HouseCanaryResponse(object):
    """Encapsulate an http response from the HouseCanary API."""

    def __init__(self, body=None, status_code=None, request_info=None):
        """ Initialize the response object's data.

        Args:
            body (str) -- The response body. Optional.
            status_code (int) -- The http status code. Optional.
            request_info (dict) -- Details of the request that was made. Optional.
        """
        self._body = body
        self._status_code = status_code
        self._request_info = request_info
        self._hc_properties = []
        self._has_business_error = None
        self._business_error_messages = None

    @classmethod
    def create_from_http_response(cls, http_response, request_info):
        """Create a HouseCanaryResponse object from an http response

        Args:
            http_response (response object) - The response from the http request.
            request_info (dict) - Details of the request that was made.

        Returns:
            HouseCanaryResponse object
        """
        response_body = http_response.read()

        status_code = http_response.getcode()

        hc_response = cls(response_body, status_code, request_info)
        return hc_response

    def body(self):
        """Gets the response body string

        Returns:
            Response body string.
        """
        return self._body

    def body_json(self):
        """Gets the response body as json, or just the body string if it's not valid json.

        Returns:
            Json dict of the response body, or string of the response body if not valid json.
        """
        try:
            return json.loads(self._body)
        except (TypeError, ValueError):
            return self._body

    def status_code(self):
        """Gets the http status code.

        Returns:
            int
        """
        return self._status_code

    def request_info(self):
        """Gets the original request information as json.
        Contains the endpoint, http method, query params and post data.

        Returns:
            dict
        """
        return self._request_info

    def method(self):
        """Gets the http method of the original request

        Returns:
            string
        """
        return self._request_info["method"]

    def get_business_error_messages(self):
        """Gets a list of business error message strings
        for each of the requested properties that had a business error.
        If there was no error, returns an empty list

        Returns:
            List of strings
        """
        if self._business_error_messages is None:
            self._business_error_messages = [{p.unique_id: p.get_business_error()}
                                             for p in self.hc_properties()
                                             if p.has_business_error()]

        return self._business_error_messages

    def has_business_error(self):
        """Returns true if any requested address had a business logic error,
        otherwise returns false

        Returns:
            boolean
        """
        if self._has_business_error is None:
            # scan the hc_properties for any business error codes
            self._has_business_error = next(
                (True for p in self.hc_properties()
                 if p.has_business_error()),
                False)
        return self._has_business_error

    def hc_properties(self):
        """Gets a list of HouseCanaryProperty objects for the requested properties,
        each containing the property's returned json data from the API.

        Returns an empty list if the request format was PDF.

        Returns:
            List of HouseCanaryProperty objects
        """
        if not self._hc_properties:
            body_json = self.body_json()
            if not isinstance(body_json, dict):
                return []

            props = []

            if self.method() == "GET":
                # response structure has just one address
                # no unique_id was passed in for this, so just create a random one.
                unique_id = str(uuid.uuid4())
                prop = HouseCanaryProperty.create_from_json(unique_id, body_json)
                props.append(prop)
            else:
                # response structure has multiple addresses with unique_id keys
                for unique_id in body_json.keys():
                    prop = HouseCanaryProperty.create_from_json(unique_id, body_json[unique_id])
                    props.append(prop)

            self._hc_properties = props
        return self._hc_properties
