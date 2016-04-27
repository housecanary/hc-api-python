"""
housecanary.output

This module provides the HouseCanaryResponse object, which encapsulates
a response from the HouseCanary API.

"""

from housecanary.hcobject import HouseCanaryProperty


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
        self._hc_objects = []
        self._has_object_error = None
        self._object_errors = None

    @classmethod
    def create(cls, endpoint_name, json_body, original_response):
        """Factory method for creating the correct type of HouseCanaryResponse based on the data.
        Args:
            endpoint_name (str) - The endpoint of the request, such as "property/value"
            json_body - The response body in json format.
            original_response (response object) - server response returned from an http request.
        """
        # Eventually, this will check the json_body to create other types.
        return HouseCanaryPropertyResponse(endpoint_name, json_body, original_response)

    @property
    def endpoint_name(self):
        """Get the endpoint name of the original request.

        Returns:
            Endpoint name as a string.
        """
        return self._endpoint_name

    @property
    def response(self):
        """Gets the original response

        Returns:
            response object passed in during instantiation.
        """
        return self._response

    def json(self):
        """Gets the response body as json

        Returns:
            Json of the response body
        """
        return self._json_body

    def get_object_errors(self):
        """Gets a list of business error message strings
        for each of the requested objects that had a business error.
        If there was no error, returns an empty list

        Returns:
            List of strings
        """
        if self._object_errors is None:
            self._object_errors = [{str(o): o.get_error()}
                                   for o in self.hc_objects()
                                   if o.has_error()]

        return self._object_errors

    def has_object_error(self):
        """Returns true if any requested object had a business logic error,
        otherwise returns false

        Returns:
            boolean
        """
        if self._has_object_error is None:
            # scan the hc_objects for any business error codes
            self._has_object_error = next(
                (True for o in self.hc_objects()
                 if o.has_error()),
                False)
        return self._has_object_error

    def hc_objects(self):
        """Override in subclasses"""
        raise NotImplementedError()

class HouseCanaryPropertyResponse(HouseCanaryResponse):
    """Represents a single property and its data returned from the API."""
    def hc_objects(self):
        """Gets a list of HouseCanaryProperty objects for the requested properties,
        each containing the property's returned json data from the API.

        Returns an empty list if the request format was PDF.

        Returns:
            List of HouseCanaryProperty objects
        """
        if not self._hc_objects:
            body = self.json()

            self._hc_objects = []

            if not isinstance(body, list):
                # The API always returns a list in the body. This could maybe raise exception.
                return []

            for address in body:
                hc_property = HouseCanaryProperty.create_from_json(self.endpoint_name, address)
                self._hc_objects.append(hc_property)

        return self._hc_objects

    def hc_properties(self):
        """Alias method for hc_objects."""
        return self.hc_objects()


class HouseCanaryZipcodeResponse(HouseCanaryResponse):
    """To be implemented later."""
    pass


class HouseCanaryLatLngResponse(HouseCanaryResponse):
    """To be implemented later."""
    pass
