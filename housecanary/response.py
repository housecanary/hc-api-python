"""
Provides Response to encapsulate API responses.
"""

from housecanary.object import Property
from housecanary.object import Block
from housecanary.object import ZipCode
from . import utilities


class Response(object):
    """Encapsulate an API reponse."""

    def __init__(self, endpoint_name, json_body, original_response):
        """
        Args:
            endpoint_name (str) - The endpoint of the request, such as "property/value"
            json_body - The response body in json format.
            original_response (response object) - server response returned from an http request.
        """
        self._endpoint_name = endpoint_name
        self._json_body = json_body
        self._response = original_response
        self._objects = []
        self._has_object_error = None
        self._object_errors = None
        self._rate_limits = None

    @classmethod
    def create(cls, endpoint_name, json_body, original_response):
        """Factory for creating the correct type of Response based on the data.
        Args:
            endpoint_name (str) - The endpoint of the request, such as "property/value"
            json_body - The response body in json format.
            original_response (response object) - server response returned from an http request.
        """

        if endpoint_name == "property/value_report":
            return ValueReportResponse(endpoint_name, json_body, original_response)

        if endpoint_name == "property/rental_report":
            return RentalReportResponse(endpoint_name, json_body, original_response)

        prefix = endpoint_name.split("/")[0]

        if prefix == "block":
            return BlockResponse(endpoint_name, json_body, original_response)

        if prefix == "zip":
            return ZipCodeResponse(endpoint_name, json_body, original_response)

        return PropertyResponse(endpoint_name, json_body, original_response)

    @property
    def endpoint_name(self):
        """Get the component name of the original request.

        Returns:
            Component name as a string.
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
            self._object_errors = [{str(o): o.get_errors()}
                                   for o in self.objects()
                                   if o.has_error()]

        return self._object_errors

    def has_object_error(self):
        """Returns true if any requested object had a business logic error,
        otherwise returns false

        Returns:
            boolean
        """
        if self._has_object_error is None:
            # scan the objects for any business error codes
            self._has_object_error = next(
                (True for o in self.objects()
                 if o.has_error()),
                False)
        return self._has_object_error

    def objects(self):
        """Override in subclasses"""
        raise NotImplementedError()

    @property
    def rate_limits(self):
        """Returns a list of rate limit details."""
        if not self._rate_limits:
            self._rate_limits = utilities.get_rate_limits(self.response)

        return self._rate_limits


class PropertyResponse(Response):
    """Represents the data returned from an Analytics API property endpoint."""

    def objects(self):
        """Gets a list of Property objects for the requested properties,
        each containing the property's returned json data from the API.

        Returns an empty list if the request format was PDF.

        Returns:
            List of Property objects
        """
        if not self._objects:
            body = self.json()

            self._objects = []

            if not isinstance(body, list):
                # The property endpoints return a list in the body.
                # This could maybe raise an exception.
                return []

            for address in body:
                prop = Property.create_from_json(address)
                self._objects.append(prop)

        return self._objects

    def properties(self):
        """Alias method for objects."""
        return self.objects()


class BlockResponse(Response):
    """Represents the data returned from an Analytics API block endpoint."""

    def objects(self):
        """Gets a list of Block objects for the requested blocks,
        each containing the block's returned json data from the API.

        Returns:
            List of Block objects
        """
        if not self._objects:
            body = self.json()

            self._objects = []

            if not isinstance(body, list):
                # The block endpoints return a list in the body.
                # This could maybe raise an exception.
                return []

            for block in body:
                prop = Block.create_from_json(block)
                self._objects.append(prop)

        return self._objects

    def blocks(self):
        """Alias method for objects."""
        return self.objects()


class ZipCodeResponse(Response):
    """Represents the data returned from an Analytics API zip endpoint."""

    def objects(self):
        """Gets a list of ZipCode objects for the requested zipcodes,
        each containing the zipcodes's returned json data from the API.

        Returns:
            List of ZipCode objects
        """
        if not self._objects:
            body = self.json()

            self._objects = []

            if not isinstance(body, list):
                # The zip endpoints return a list in the body.
                # This could maybe raise an exception.
                return []

            for zip in body:
                prop = ZipCode.create_from_json(zip)
                self._objects.append(prop)

        return self._objects

    def zipcodes(self):
        """Alias method for objects."""
        return self.objects()


class ZipcodeResponse(Response):
    """To be implemented later."""
    pass


class LatLngResponse(Response):
    """To be implemented later."""
    pass


class ValueReportResponse(Response):
    """The response from a value_report request."""

    def objects(self):
        """The value_report endpoint returns a json dict
           instead of a list of address results."""
        return []


class RentalReportResponse(Response):
    """The response from a rental_report request."""

    def objects(self):
        """The rental_report endpoint returns a json dict
           instead of a list of address results."""
        return []
