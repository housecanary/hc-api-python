import os
from housecanary.output import ResponseOutputGenerator
from housecanary.requestclient import RequestClient
import housecanary.exceptions
import housecanary.constants as constants
from requests.auth import HTTPBasicAuth


class ApiClient(object):
    """Base class for making API calls"""

    def __init__(self, auth_key=None, auth_secret=None, version=None, request_client=None,
                 output_generator=None, auth=None):
        """
        auth_key and auth_secret can be passed in as parameters or
        pulled automatically from the following environment variables:
            HC_API_KEY -- Your HouseCanary API auth key
            HC_API_SECRET -- Your HouseCanary API secret

        Passing in the key and secret as parameters will take precedence over environment variables.

        Args:
            auth_key - Optional. The HouseCanary API auth key.
            auth_secret - Optional. The HouseCanary API secret.
            version (str) - Optional. The API version to use, in the form "v2", for example.
                            Default is "v2".
            request_client - Optional. An instance of a class that is responsible for
                             making http requests. It must implement a `post` method.
                             Default is RequestClient.
            output_generator - Optional. An instance of an OutputGenerator that implements
                               a `process_response` method. Can be used to implement custom
                               serialization of the response data from the request client.
                               Default is ResponseOutputGenerator.
            authenticator - Optional. An instance of a requests.auth.AuthBase implementation
                            for providing authentication to the request.
                            Default is requests.auth.HTTPBasicAuth.
        """

        self._auth_key = auth_key or os.environ['HC_API_KEY']
        self._auth_secret = auth_secret or os.environ['HC_API_SECRET']

        self._version = version or constants.DEFAULT_VERSION

        # user can pass in a custom request_client
        self._request_client = request_client

        # if no request_client provided, use the defaults.
        if self._request_client is None:
            # allow using custom OutputGenerator or Authenticator with the RequestClient
            _output_generator = output_generator or ResponseOutputGenerator()
            _auth = auth or HTTPBasicAuth(self._auth_key, self._auth_secret)
            self._request_client = RequestClient(_output_generator, _auth)

        self.property = PropertyComponentWrapper(self)

    def fetch(self, endpoint_name, post_data, query_params=None):
        """Calls this instance's request_client's post method with the
        specified component endpoint

        Args:
            - endpoint_name (str) - The endpoint to call like "property/value".
            - address_data - One or more address to request data for. Address data can
                             be in one of these forms:

                            - A Json formatted list like:
                            [{"address":"82 County Line Rd",
                              "zipcode":"72173",
                              "meta":"extra info"}]

                                - A list of (address, zipcode, meta) tuples like:
                                [("82 County Line Rd", "72173", "extra info")]

                                - A single address tuple:
                                ("82 County Line Rd", "72173", "extra_info")

                                The "meta" field is optional.

        Returns:
            A Response object, or the output of a custom OutputGenerator
            if one was specified in the constructor.
        """

        endpoint_url = constants.URL_PREFIX + "/" + self._version + "/" + endpoint_name

        if query_params is None:
            query_params = {}

        if len(post_data) == 1:
            # If only one address specified, use a GET request
            query_params.update(post_data[0])
            return self._request_client.get(endpoint_url, query_params)

        # when more than one address, use a POST request
        return self._request_client.post(endpoint_url, post_data, query_params)

    def fetch_synchronous(self, endpoint_name, query_params=None):
        """Calls this instance's request_client's get method with the
        specified component endpoint"""

        endpoint_url = constants.URL_PREFIX + "/" + self._version + "/" + endpoint_name

        if query_params is None:
            query_params = {}

        return self._request_client.get(endpoint_url, query_params)


class PropertyComponentWrapper(object):
    """Property specific components

    All the component methods of this class take address data as parameter. Address data can
    be in one of two forms:

        - A Json formatted list like:
        [{"address":"82 County Line Rd", "zipcode":"72173", "meta":"extra info"}]

        - A list of (address, zipcode, meta) tuples like:
        [("82 County Line Rd", "72173", "extra info")]

        The "meta" field is optional.

    All the component methods of this class return a Response object,
    or the output of a custom OutputGenerator if one was specified in the constructor.
    """

    def __init__(self, api_client=None):
        """
        Args:
            - api_client - An instances of ApiClient
        """
        self._api_client = api_client

    def fetch_property_component(self, endpoint_name, address_data, query_params=None):
        """common method for handling parameters before passing to api_client"""

        if query_params is None:
            query_params = {}

        post_data = get_post_data(address_data)

        return self._api_client.fetch(endpoint_name, post_data, query_params)

    def census(self, address_data):
        """Call the census endpoint"""
        return self.fetch_property_component("property/census", address_data)

    def details(self, address_data):
        """Call the details endpoint"""
        return self.fetch_property_component("property/details", address_data)

    def flood(self, address_data):
        """Call the flood endpoint"""
        return self.fetch_property_component("property/flood", address_data)

    def mortgage_lien(self, address_data):
        """Call the mortgage_lien endpoint"""
        return self.fetch_property_component("property/mortgage_lien", address_data)

    def msa_details(self, address_data):
        """Call the msa_details endpoint"""
        return self.fetch_property_component("property/msa_details", address_data)

    def nod(self, address_data):
        """Call the nod endpoint"""
        return self.fetch_property_component("property/nod", address_data)

    def owner_occupied(self, address_data):
        """Call the owner_occupied endpoint"""
        return self.fetch_property_component("property/owner_occupied", address_data)

    def rental_value(self, address_data):
        """Call the rental_value endpoint"""
        return self.fetch_property_component("property/rental_value", address_data)

    def sales_history(self, address_data):
        """Call the sales_history endpoint"""
        return self.fetch_property_component("property/sales_history", address_data)

    def school(self, address_data):
        """Call the school endpoint"""
        return self.fetch_property_component("property/school", address_data)

    def value(self, address_data):
        """Call the value endpoint"""
        return self.fetch_property_component("property/value", address_data)

    def value_forecast(self, address_data):
        """Call the value_forecast endpoint"""
        return self.fetch_property_component("property/value_forecast", address_data)

    def zip_details(self, address_data):
        """Call the zip_details endpoint"""
        return self.fetch_property_component("property/zip_details", address_data)

    def zip_hpi_forecast(self, address_data):
        """Call the zip_hpi_forecast endpoint"""
        return self.fetch_property_component("property/zip_hpi_forecast", address_data)

    def zip_hpi_historical(self, address_data):
        """Call the zip_hpi_historical endpoint"""
        return self.fetch_property_component("property/zip_hpi_historical", address_data)

    def zip_volatility(self, address_data):
        """Call the zip_volatility endpoint"""
        return self.fetch_property_component("property/zip_volatility", address_data)

    def component_mget(self, address_data, components):
        """Call the component_mget endpoint

        Args:
            - address_data - As described in the class docstring.
            - components - A list of strings for each component to include in the request.
                Example: ["property/details", "property/flood", "property/value"]
        """
        if not isinstance(components, list):
            print "Components param must be a list"
            return

        query_params = {"components": ",".join(components)}

        return self.fetch_property_component("property/component_mget", address_data, query_params)

    def value_report(self, address, zipcode, report_type="full", format_type="json"):
        """Call the value_report component

        Value Report only supports a single address.

        Args:
            - address
            - zipcode

        Kwargs:
            - report_type - "full" or "summary". Default is "full".
            - format_type - "json", "pdf", "xlsx" or "all". Default is "json".
        """
        query_params = {
            "report_type": report_type,
            "format": format_type,
            "address": address,
            "zipcode": zipcode
        }

        return self._api_client.fetch_synchronous("property/value_report", query_params)

    def rental_report(self, address, zipcode, format_type="json"):
        """Call the rental_report component

        Rental Report only supports a single address.

        Args:
            - address
            - zipcode

        Kwargs:
            - format_type - "json", "xlsx" or "all". Default is "json".
        """

        # only json is supported by rental report.
        query_params = {
            "format": format_type,
            "address": address,
            "zipcode": zipcode
        }

        return self._api_client.fetch_synchronous("property/rental_report", query_params)


def get_post_data(address_data):
    """Convert the various formats of input address_data into
    the proper json format expected by the API."""

    post_data = []

    if isinstance(address_data, list) and len(address_data) > 0:
        # if list, convert each address in the list to json
        for address in address_data:
            post_data.append(convert_to_json(address))
    else:
        post_data.append(convert_to_json(address_data))

    return post_data


def convert_to_json(address_data):
    """Convert input address tuples into json format"""

    if address_data and isinstance(address_data, str):
        # allow just passing an address string, for future support.
        # The api currently requires a zipcode as well, but may not in the future.
        address_json = {}
        address_json["address"] = address_data
        return address_json

    if isinstance(address_data, tuple) and len(address_data) > 0:
        address_json = {}
        address_json["address"] = address_data[0]
        if len(address_data) > 1:
            address_json["zipcode"] = address_data[1]
        if len(address_data) > 2:
            address_json["meta"] = address_data[2]
        return address_json

    elif isinstance(address_data, dict):
        allowed_keys = ["address", "zipcode", "meta"]

        # ensure the dict does not contain any unallowed keys
        for key in address_data:
            if key not in allowed_keys:
                msg = "Key in address input not allowed: " + key
                raise housecanary.exceptions.InvalidInputException(msg)

        # ensure it contains an "address" key
        if "address" in address_data:
            return address_data

    # if we made it here, the input was not valid.
    msg = ("Input is invalid. Must be a list of (address, zipcode) tuples,"
           " or a Json formatted list with each item containing at least an 'address' key.")
    raise housecanary.exceptions.InvalidInputException((msg))
