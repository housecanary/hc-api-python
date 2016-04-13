"""
housecanary.hcapiclient

This module provides the main classes for HouseCanary API access.
"""

import os
from housecanary.authentication import HCAuthV1
from housecanary.output import HCResponseOutputGenerator
from housecanary.hcrequests import HouseCanaryRequestClient
import housecanary.exceptions

class ApiClient(object):
    """The base class for making API calls"""

    KEY_ENV_VAR = "HC_API_KEY"
    SECRET_ENV_VAR = "HC_API_SECRET"
    URL_PREFIX = "https://api-branch.housecanary.net"
    DEFAULT_VERSION = "v2"

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
            output_generator - Optional. An instance of an OutputGenerator used
                               to process the response from the server request and return
                               an object from the execute_request method. Can be used
                               to implement custom serialization of the response data.
                               Default is HCResponseOutputGenerator.
            authenticator - Optional. An instance of a requests.auth.AuthBase implementation
                            for providing authentication to the request.
                            Default is HCAuthV1.
        """

        self._auth_key = auth_key or os.environ[self.KEY_ENV_VAR]
        self._auth_secret = auth_secret or os.environ[self.SECRET_ENV_VAR]

        self._version = version or self.DEFAULT_VERSION
        
        # user can pass in a custom request_client
        self._request_client = request_client

        # if no request_client provided, use the defaults.
        if self._request_client is None:
            # allow using custom OutputGenerator or Authenticator with the HouseCanaryRequestClient
            _output_generator = output_generator or HCResponseOutputGenerator()
            _auth = auth or HCAuthV1(self._auth_key, self._auth_secret)
            self._request_client = HouseCanaryRequestClient(_output_generator, _auth)

    def fetch(self, endpoint_name, post_data):
        endpoint_url = self.URL_PREFIX + "/" + self._version + "/" + endpoint_name
        return self._request_client.post(endpoint_url, post_data)

class PropertyApiClient(ApiClient):
    """The client class for calling the HouseCanary Property API

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
    def _convert_to_json(self, address_data):
        if address_data and isinstance(address_data, str):
            # allow just passing an address string, for future support.
            # The api currently requires a zipcode as well, but may not in the future.
            address_json = {}
            address_json["address"] = address_data
            return address_json
        if isinstance(address_data, tuple) and len(address_data) > 0:
            address_json = {}
            address_json["address"] = address_data[0]
            if len(address_data) > 1: address_json["zipcode"] = address_data[1]
            if len(address_data) > 2: address_json["meta"] = address_data[2]
            return address_json

        elif isinstance(address_data, dict):
            # if it's already a dict, just ensure it contains an "address" key
            if "address" in address_data:
                return address_data

        # if we made it here, the input was not valid.
        msg = ("Input is invalid. Must be a list of (address, zipcode) tuples," 
               " or a Json formatted list with each item containing at least an 'address' key.")
        raise housecanary.exceptions.InvalidInputException((msg))


    def consumer(self, address_data):
        """Call the consumer endpoint"""
        return self.fetch("property/consumer", self._get_post_data(address_data))

    def flood(self, address_data):
        """Call the flood endpoint"""
        return self.fetch("property/flood", self._get_post_data(address_data))

    def school(self, address_data):
        """Call the school endpoint"""
        return self.fetch("property/school", self._get_post_data(address_data))

    def value(self, address_data):
        """Call the value endpoint"""
        return self.fetch("property/avm", self._get_post_data(address_data))

    def value_forecast(self, address_data):
        """Call the value_forecast endpoint"""
        return self.fetch("property/value_forecast", self._get_post_data(address_data))

    def score(self, address_data):
        """Call the score endpoint"""
        return self.fetch("property/score", self._get_post_data(address_data))

    def zip_hpi_historical(self, address_data):
        """Call the zip_hpi_historical endpoint"""
        return self.fetch("property/zip_hpi_historical", self._get_post_data(address_data))

    def zip_hpi_forecast(self, address_data):
        """Call the zip_hpi_forecast endpoint"""
        return self.fetch("property/zip_hpi_forecast", self._get_post_data(address_data))

    def rental_value(self, address_data):
        """Call the rental_value endpoint"""
        return self.fetch("property/rental_value", self._get_post_data(address_data))

    def msa_details(self, address_data):
        """Call the msa_details endpoint"""
        return self.fetch("property/msa_details", self._get_post_data(address_data))

    def mortgage_lien(self, address_data):
        """Call the mortgage_lien endpoint"""
        return self.fetch("property/mortgage_lien", self._get_post_data(address_data))

    def ltv(self, address_data):
        """Call the ltv endpoint"""
        return self.fetch("property/ltv", self._get_post_data(address_data))

    def ltv_forecast(self, address_data):
        """Call the ltv_forecast endpoint"""
        return self.fetch("property/ltv_forecast", self._get_post_data(address_data))

    def owner_occupied(self, address_data):
        """Call the owner_occupied endpoint"""
        return self.fetch("property/owner_occupied", self._get_post_data(address_data))

    def details(self, address_data):
        """Call the details endpoint"""
        return self.fetch("property/details", self._get_post_data(address_data))

    def sales_history(self, address_data):
        """Call the sales_history endpoint"""
        return self.fetch("property/sales_history", self._get_post_data(address_data))

    def mls(self, address_data):
        """Call the mls endpoint"""
        return self.fetch("property/mls", self._get_post_data(address_data))

    def nod(self, address_data):
        """Call the nod endpoint"""
        return self.fetch("property/nod", self._get_post_data(address_data))

    def census(self, address_data):
        """Call the census endpoint"""
        return self.fetch("property/census", self._get_post_data(address_data))
