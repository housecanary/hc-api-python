"""
housecanary.hcapiclient

This module provides the main classes for HouseCanary API access.
"""

import os
from housecanary.authentication import HCAuthV1
from housecanary.output import HCResponseOutputGenerator
from housecanary.hcrequests import HouseCanaryRequestClient
import housecanary.exceptions
import housecanary.constants as hcconstants

class ApiClient(object):
    """The base class for making API calls"""

    def __init__(self, auth_key=None, auth_secret=None, version=None, request_client=None,
                 output_generator=None, auth=None):
        """Constructor

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
                             Default is HouseCanaryRequestClient.
            output_generator - Optional. An instance of an OutputGenerator that implements
                               a `process_response` method. Can be used to implement custom
                               serialization of the response data from the request client.
                               Default is HCResponseOutputGenerator.
            authenticator - Optional. An instance of a requests.auth.AuthBase implementation
                            for providing authentication to the request.
                            Default is HCAuthV1.
        """

        self._auth_key = auth_key or os.environ[hcconstants.KEY_ENV_VAR]
        self._auth_secret = auth_secret or os.environ[hcconstants.SECRET_ENV_VAR]

        self._version = version or hcconstants.DEFAULT_VERSION

        # user can pass in a custom request_client
        self._request_client = request_client

        # if no request_client provided, use the defaults.
        if self._request_client is None:
            # allow using custom OutputGenerator or Authenticator with the HouseCanaryRequestClient
            _output_generator = output_generator or HCResponseOutputGenerator()
            _auth = auth or HCAuthV1(self._auth_key, self._auth_secret)
            self._request_client = HouseCanaryRequestClient(_output_generator, _auth)

        self._address_wrapper = AddressEndpointWrapper(self)

    def fetch(self, endpoint_name, address_data):
        """Calls this instance's request_client's post method with the
        specified endpoint and the specified address_data

        Args:
            - endpoint_name (str) - The endpoint to call like "property/score".
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
            A HouseCanaryResponse object, or the output of a custom OutputGenerator
            if one was specified in the constructor.
        """
        endpoint_url = hcconstants.URL_PREFIX + "/" + self._version + "/" + endpoint_name
        return self._request_client.post(endpoint_url, self._get_post_data(address_data))

    def _get_post_data(self, address_data):
        post_data = []

        if isinstance(address_data, list) and len(address_data) > 0:
            # if list, convert each address in the list to json
            for address in address_data:
                post_data.append(self._convert_to_json(address))
        else:
            post_data.append(self._convert_to_json(address_data))

        return post_data

    # convert input address tuples into json format
    @staticmethod
    def _convert_to_json(address_data):
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

    @property
    def address(self):
        return self._address_wrapper

class AddressEndpointWrapper(object):
    """A class for encapsulating Address specific endpoints of the HouseCanary API

    All the endpoint methods of this class take address data as parameter. Address data can
    be in one of two forms:

        - A Json formatted list like:
        [{"address":"82 County Line Rd", "zipcode":"72173", "meta":"extra info"}]

        - A list of (address, zipcode, meta) tuples like:
        [("82 County Line Rd", "72173", "extra info")]

        The "meta" field is optional.

    All the endpoint methods of this class return a HouseCanaryResponse object,
    or the output of a custom OutputGenerator if one was specified in the constructor.
    """

    def __init__(self, api_client=None):
        """Constructor.

        Args:
            - api_client - An instances of ApiClient
        """
        self._api_client = api_client

    def consumer(self, address_data):
        """Call the consumer endpoint"""
        return self._api_client.fetch("property/consumer", address_data)

    def flood(self, address_data):
        """Call the flood endpoint"""
        return self._api_client.fetch("property/flood", address_data)

    def school(self, address_data):
        """Call the school endpoint"""
        return self._api_client.fetch("property/school", address_data)

    def value(self, address_data):
        """Call the value endpoint"""
        return self._api_client.fetch("property/value", address_data)

    def value_forecast(self, address_data):
        """Call the value_forecast endpoint"""
        return self._api_client.fetch("property/value_forecast", address_data)

    def score(self, address_data):
        """Call the score endpoint"""
        return self._api_client.fetch("property/score", address_data)

    def zip_hpi_historical(self, address_data):
        """Call the zip_hpi_historical endpoint"""
        return self._api_client.fetch("property/zip_hpi_historical", address_data)

    def zip_hpi_forecast(self, address_data):
        """Call the zip_hpi_forecast endpoint"""
        return self._api_client.fetch("property/zip_hpi_forecast", address_data)

    def rental_value(self, address_data):
        """Call the rental_value endpoint"""
        return self._api_client.fetch("property/rental_value", address_data)

    def msa_details(self, address_data):
        """Call the msa_details endpoint"""
        return self._api_client.fetch("property/msa_details", address_data)

    def mortgage_lien(self, address_data):
        """Call the mortgage_lien endpoint"""
        return self._api_client.fetch("property/mortgage_lien", address_data)

    def ltv(self, address_data):
        """Call the ltv endpoint"""
        return self._api_client.fetch("property/ltv", address_data)

    def ltv_forecast(self, address_data):
        """Call the ltv_forecast endpoint"""
        return self._api_client.fetch("property/ltv_forecast", address_data)

    def owner_occupied(self, address_data):
        """Call the owner_occupied endpoint"""
        return self._api_client.fetch("property/owner_occupied", address_data)

    def details(self, address_data):
        """Call the details endpoint"""
        return self._api_client.fetch("property/details", address_data)

    def sales_history(self, address_data):
        """Call the sales_history endpoint"""
        return self._api_client.fetch("property/sales_history", address_data)

    def mls(self, address_data):
        """Call the mls endpoint"""
        return self._api_client.fetch("property/mls", address_data)

    def nod(self, address_data):
        """Call the nod endpoint"""
        return self._api_client.fetch("property/nod", address_data)

    def census(self, address_data):
        """Call the census endpoint"""
        return self._api_client.fetch("property/census", address_data)
