"""
housecanary.output

This module provides the HouseCanaryResponse object, which encapsulates
a response from the HouseCanary API.

"""

from housecanary.hcproperty import HouseCanaryProperty

class HouseCanaryResponse(object):
    """Encapsulate an http response from the HouseCanary API."""

    def __init__(self, endpoint_name, json_body, original_response):
        """ Initialize the response object's data.

        Args:
            endpoint_name (str) - The endpoint of the request, such as "property/value"
            json_body - The response body in json format.
            original_response (response object) - server response returned from an http request.
        """
        self._endpoint_name = endpoint_name
        self._json_body = json_body
        self._response = original_response
        self._hc_properties = []
        self._has_property_error = None
        self._property_errors = None

    @property
    def endpoint_name(self):
        """Get the endpoint name of the original request.

        Returns:
            Endpoint name as a string.
        """
        return self._endpoint_name

    @property
    def json_body(self):
        """Gets the response body as json

        Returns:
            Json of the response body
        """
        return self._json_body

    @property
    def response(self):
        """Gets the original response

        Returns:
            response object passed in during instantiation.
        """
        return self._response

    def get_property_errors(self):
        """Gets a list of business error message strings
        for each of the requested properties that had a business error.
        If there was no error, returns an empty list

        Returns:
            List of strings
        """
        if self._property_errors is None:
            self._property_errors = [{p.address: p.get_property_error()}
                                             for p in self.hc_properties()
                                             if p.has_property_error()]

        return self._property_errors

    def has_property_error(self):
        """Returns true if any requested address had a business logic error,
        otherwise returns false

        Returns:
            boolean
        """
        if self._has_property_error is None:
            # scan the hc_properties for any business error codes
            self._has_property_error = next(
                (True for p in self.hc_properties()
                 if p.has_property_error()),
                False)
        return self._has_property_error

    def hc_properties(self):
        """Gets a list of HouseCanaryProperty objects for the requested properties,
        each containing the property's returned json data from the API.

        Returns an empty list if the request format was PDF.

        Returns:
            List of HouseCanaryProperty objects
        """
        if not self._hc_properties:
            body = self.json_body

            self._hc_properties = []

            if not isinstance(body, list):
                # The API always returns a list in the body. This could maybe raise exception.
                return []

            for address in body:
                hc_property = HouseCanaryProperty.create_from_json(self.endpoint_name, address)
                self._hc_properties.append(hc_property)

        return self._hc_properties
