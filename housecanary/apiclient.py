from __future__ import print_function
import os
from builtins import object
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

        self._auth_key = auth_key or os.getenv('HC_API_KEY')
        self._auth_secret = auth_secret or os.getenv('HC_API_SECRET')

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
        self.block = BlockComponentWrapper(self)
        self.zip = ZipComponentWrapper(self)
        self.msa = MsaComponentWrapper(self)

    def fetch(self, endpoint_name, identifier_input, query_params=None):
        """Calls this instance's request_client's post method with the
        specified component endpoint

        Args:
            - endpoint_name (str) - The endpoint to call like "property/value".
            - identifier_input - One or more identifiers to request data for. An identifier can
                be in one of these forms:

                - A list of property identifier dicts:
                    - A property identifier dict can contain the following keys:
                      (address, zipcode, unit, city, state, slug, meta).
                      One of 'address' or 'slug' is required.

                      Ex: [{"address": "82 County Line Rd",
                           "zipcode": "72173",
                           "meta": "some ID"}]

                      A slug is a URL-safe string that identifies a property.
                      These are obtained from HouseCanary.

                      Ex: [{"slug": "123-Example-St-San-Francisco-CA-94105"}]

                - A list of dicts representing a block:
                  - A block identifier dict can contain the following keys:
                      (block_id, num_bins, property_type, meta).
                      'block_id' is required.

                  Ex: [{"block_id": "060750615003005", "meta": "some ID"}]

                - A list of dicts representing a zipcode:

                  Ex: [{"zipcode": "90274", "meta": "some ID"}]

                - A list of dicts representing an MSA:

                  Ex: [{"msa": "41860", "meta": "some ID"}]

                The "meta" field is always optional.

        Returns:
            A Response object, or the output of a custom OutputGenerator
            if one was specified in the constructor.
        """

        endpoint_url = constants.URL_PREFIX + "/" + self._version + "/" + endpoint_name

        if query_params is None:
            query_params = {}

        if len(identifier_input) == 1:
            # If only one identifier specified, use a GET request
            query_params.update(identifier_input[0])
            return self._request_client.get(endpoint_url, query_params)

        # when more than one address, use a POST request
        return self._request_client.post(endpoint_url, identifier_input, query_params)

    def fetch_synchronous(self, endpoint_name, query_params=None):
        """Calls this instance's request_client's get method with the
        specified component endpoint"""

        endpoint_url = constants.URL_PREFIX + "/" + self._version + "/" + endpoint_name

        if query_params is None:
            query_params = {}

        return self._request_client.get(endpoint_url, query_params)


class ComponentWrapper(object):
    def __init__(self, api_client=None):
        """
        Args:
            - api_client - An instance of ApiClient
        """
        self._api_client = api_client

    def _convert_to_identifier_json(self, identifier_data):
        """Override in subclasses"""
        raise NotImplementedError()

    def get_identifier_input(self, identifier_data):
        """Convert the various formats of input identifier_data into
        the proper json format expected by the ApiClient fetch method,
        which is a list of dicts."""

        identifier_input = []

        if isinstance(identifier_data, list) and len(identifier_data) > 0:
            # if list, convert each item in the list to json
            for address in identifier_data:
                identifier_input.append(self._convert_to_identifier_json(address))
        else:
            identifier_input.append(self._convert_to_identifier_json(identifier_data))

        return identifier_input

    def fetch_identifier_component(self, endpoint_name, identifier_data, query_params=None):
        """Common method for handling parameters before passing to api_client"""

        if query_params is None:
            query_params = {}

        identifier_input = self.get_identifier_input(identifier_data)

        return self._api_client.fetch(endpoint_name, identifier_input, query_params)


class PropertyComponentWrapper(ComponentWrapper):
    """Property specific components

    All the component methods of this class (except value_report and rental_report)
    take data as a parameter. data can be in the following forms:

        - A dict like:
          {"address": "82 County Line Rd", "zipcode": "72173", "meta": "someID"}
          or
          {"address": "82 County Line Rd", "city": "San Francisco", "state": "CA", "meta": "someID"}
          or
          {"slug": "123-Example-St-San-Francisco-CA-94105"}

        - A list of dicts as specified above:
          [{"address": "82 County Line Rd", "zipcode": "72173", "meta": "someID"},
           {"address": "43 Valmonte Plaza", "zipcode": "90274", "meta": "someID2"}]

        - A single string representing a slug:
          "123-Example-St-San-Francisco-CA-94105"

        - A tuple in the form of (address, zipcode, meta) like:
          ("82 County Line Rd", "72173", "someID")

        - A list of (address, zipcode, meta) tuples like:
          [("82 County Line Rd", "72173", "someID"),
           ("43 Valmonte Plaza", "90274", "someID2")]

        Using a tuple only supports address, zipcode and meta. To specify city, state, unit or slug,
        please use a dict.

        The "meta" field is always optional.

        The available keys in the dict are:
            - address (required if no slug)
            - slug (required if no address)
            - zipcode (optional)
            - unit (optional)
            - city (optional)
            - state (optional)
            - meta (optional)
            - client_value (optional, for "value_within_block" and "rental_value_within_block")
            - client_value_sqft (optional, for "value_within_block" and "rental_value_within_block")

    All the component methods of this class return a PropertyResponse object,
    (or ValueReportResponse or RentalReportResponse)
    or the output of a custom OutputGenerator if one was specified in the constructor.
    """

    def _convert_to_identifier_json(self, address_data):
        """Convert input address data into json format"""

        if isinstance(address_data, str):
            # allow just passing a slug string.
            return {"slug": address_data}

        if isinstance(address_data, tuple) and len(address_data) > 0:
            address_json = {"address": address_data[0]}
            if len(address_data) > 1:
                address_json["zipcode"] = address_data[1]
            if len(address_data) > 2:
                address_json["meta"] = address_data[2]
            return address_json

        if isinstance(address_data, dict):
            allowed_keys = ["address", "zipcode", "unit", "city", "state", "slug", "meta",
                            "client_value", "client_value_sqft"]

            # ensure the dict does not contain any unallowed keys
            for key in address_data:
                if key not in allowed_keys:
                    msg = "Key in address input not allowed: " + key
                    raise housecanary.exceptions.InvalidInputException(msg)

            # ensure it contains an "address" key
            if "address" in address_data or "slug" in address_data:
                return address_data

        # if we made it here, the input was not valid.
        msg = ("Input is invalid. Must be a list of (address, zipcode) tuples, or a dict or list"
               " of dicts with each item containing at least an 'address' or 'slug' key.")
        raise housecanary.exceptions.InvalidInputException((msg))

    def block_histogram_baths(self, data):
        """Call the block_histogram_baths endpoint"""
        return self.fetch_identifier_component("property/block_histogram_baths", data)

    def block_histogram_beds(self, data):
        """Call the block_histogram_beds endpoint"""
        return self.fetch_identifier_component("property/block_histogram_beds", data)

    def block_histogram_building_area(self, data):
        """Call the block_histogram_building_area endpoint"""
        return self.fetch_identifier_component("property/block_histogram_building_area", data)

    def block_histogram_value(self, data):
        """Call the block_histogram_value endpoint"""
        return self.fetch_identifier_component("property/block_histogram_value", data)

    def block_histogram_value_sqft(self, data):
        """Call the block_histogram_value_sqft endpoint"""
        return self.fetch_identifier_component("property/block_histogram_value_sqft", data)

    def block_rental_value_distribution(self, data):
        """Call the block_rental_value_distribution endpoint"""
        return self.fetch_identifier_component("property/block_rental_value_distribution", data)

    def block_value_distribution(self, data):
        """Call the block_value_distribution endpoint"""
        return self.fetch_identifier_component("property/block_value_distribution", data)

    def block_value_ts(self, data):
        """Call the block_value_ts endpoint"""
        return self.fetch_identifier_component("property/block_value_ts", data)

    def block_value_ts_historical(self, data):
        """Call the block_value_ts_historical endpoint"""
        return self.fetch_identifier_component("property/block_value_ts_historical", data)

    def block_value_ts_forecast(self, data):
        """Call the block_value_ts_forecast endpoint"""
        return self.fetch_identifier_component("property/block_value_ts_forecast", data)

    def census(self, data):
        """Call the census endpoint"""
        return self.fetch_identifier_component("property/census", data)

    def details(self, data):
        """Call the details endpoint"""
        return self.fetch_identifier_component("property/details", data)

    def flood(self, data):
        """Call the flood endpoint"""
        return self.fetch_identifier_component("property/flood", data)

    def ltv(self, data):
        """Call the ltv endpoint"""
        return self.fetch_identifier_component("property/ltv", data)

    def ltv_details(self, data):
        """Call the ltv_details endpoint"""
        return self.fetch_identifier_component("property/ltv_details", data)

    def mortgage_lien(self, data):
        """Call the mortgage_lien endpoint"""
        return self.fetch_identifier_component("property/mortgage_lien", data)

    def msa_details(self, data):
        """Call the msa_details endpoint"""
        return self.fetch_identifier_component("property/msa_details", data)

    def msa_hpi_ts(self, data):
        """Call the msa_hpi_ts endpoint"""
        return self.fetch_identifier_component("property/msa_hpi_ts", data)

    def msa_hpi_ts_forecast(self, data):
        """Call the msa_hpi_ts_forecast endpoint"""
        return self.fetch_identifier_component("property/msa_hpi_ts_forecast", data)

    def msa_hpi_ts_historical(self, data):
        """Call the msa_hpi_ts_historical endpoint"""
        return self.fetch_identifier_component("property/msa_hpi_ts_historical", data)

    def nod(self, data):
        """Call the nod endpoint"""
        return self.fetch_identifier_component("property/nod", data)

    def owner_occupied(self, data):
        """Call the owner_occupied endpoint"""
        return self.fetch_identifier_component("property/owner_occupied", data)

    def rental_value(self, data):
        """Call the rental_value endpoint"""
        return self.fetch_identifier_component("property/rental_value", data)

    def rental_value_within_block(self, data):
        """Call the rental_value_within_block endpoint"""
        return self.fetch_identifier_component("property/rental_value_within_block", data)

    def sales_history(self, data):
        """Call the sales_history endpoint"""
        return self.fetch_identifier_component("property/sales_history", data)

    def school(self, data):
        """Call the school endpoint"""
        return self.fetch_identifier_component("property/school", data)

    def value(self, data):
        """Call the value endpoint"""
        return self.fetch_identifier_component("property/value", data)

    def value_forecast(self, data):
        """Call the value_forecast endpoint"""
        return self.fetch_identifier_component("property/value_forecast", data)

    def value_within_block(self, data):
        """Call the value_within_block endpoint"""
        return self.fetch_identifier_component("property/value_within_block", data)

    def zip_details(self, data):
        """Call the zip_details endpoint"""
        return self.fetch_identifier_component("property/zip_details", data)

    def zip_hpi_forecast(self, data):
        """Call the zip_hpi_forecast endpoint"""
        return self.fetch_identifier_component("property/zip_hpi_forecast", data)

    def zip_hpi_historical(self, data):
        """Call the zip_hpi_historical endpoint"""
        return self.fetch_identifier_component("property/zip_hpi_historical", data)

    def zip_hpi_ts(self, data):
        """Call the zip_hpi_ts endpoint"""
        return self.fetch_identifier_component("property/zip_hpi_ts", data)

    def zip_hpi_ts_forecast(self, data):
        """Call the zip_hpi_ts_forecast endpoint"""
        return self.fetch_identifier_component("property/zip_hpi_ts_forecast", data)

    def zip_hpi_ts_historical(self, data):
        """Call the zip_hpi_ts_historical endpoint"""
        return self.fetch_identifier_component("property/zip_hpi_ts_historical", data)

    def zip_volatility(self, data):
        """Call the zip_volatility endpoint"""
        return self.fetch_identifier_component("property/zip_volatility", data)

    def component_mget(self, data, components):
        """Call the component_mget endpoint

        Args:
            - data - As described in the class docstring.
            - components - A list of strings for each component to include in the request.
                Example: ["property/details", "property/flood", "property/value"]
        """
        if not isinstance(components, list):
            print("Components param must be a list")
            return

        query_params = {"components": ",".join(components)}

        return self.fetch_identifier_component(
            "property/component_mget", data, query_params)

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


class BlockComponentWrapper(ComponentWrapper):
    """Block specific components

    All the component methods of this class
    take block_data as a parameter. block_data can be in the following forms:

    - A dict with a ``block_id`` like:
        {"block_id": "060750615003005", "meta": "someId"}

    - For histogram endpoints you can include the ``num_bins`` key:
        {"block_id": "060750615003005", "num_bins": 5, "meta": "someId"}

    - For time series and distribution endpoints you can include the ``property_type`` key:
        {"block_id": "060750615003005", "property_type": "SFD", "meta": "someId"}

    - A list of dicts as specified above:
        [{"block_id": "012345678901234", "meta": "someId"},
         {"block_id": "012345678901234", "meta": "someId2}]

    - A single string representing a ``block_id``:
        "012345678901234"

    - A list of ``block_id`` strings:
        ["012345678901234", "060750615003005"]

    The "meta" field is always optional.

    All the component methods of this class return a BlockResponse object,
    or the output of a custom OutputGenerator if one was specified in the constructor.
    """

    def _convert_to_identifier_json(self, block_data):
        if isinstance(block_data, str):
            # allow just passing a block_id string.
            return {"block_id": block_data}

        if isinstance(block_data, dict):
            allowed_keys = ["block_id", "num_bins", "property_type", "meta"]

            # ensure the dict does not contain any unallowed keys
            for key in block_data:
                if key not in allowed_keys:
                    msg = "Key in block input not allowed: " + key
                    raise housecanary.exceptions.InvalidInputException(msg)

            # ensure it contains a "block_id" key
            if "block_id" in block_data:
                return block_data

        # if we made it here, the input was not valid.
        msg = ("Input is invalid. Must be a dict or list of dicts"
               " with each item containing at least 'block_id' key.")
        raise housecanary.exceptions.InvalidInputException((msg))

    def histogram_baths(self, block_data):
        """Call the histogram_baths endpoint"""
        return self.fetch_identifier_component("block/histogram_baths", block_data)

    def histogram_beds(self, block_data):
        """Call the histogram_beds endpoint"""
        return self.fetch_identifier_component("block/histogram_beds", block_data)

    def histogram_building_area(self, block_data):
        """Call the histogram_building_area endpoint"""
        return self.fetch_identifier_component("block/histogram_building_area", block_data)

    def histogram_value(self, block_data):
        """Call the histogram_value endpoint"""
        return self.fetch_identifier_component("block/histogram_value", block_data)

    def histogram_value_sqft(self, block_data):
        """Call the histogram_value_sqft endpoint"""
        return self.fetch_identifier_component("block/histogram_value_sqft", block_data)

    def rental_value_distribution(self, block_data):
        """Call the rental_value_distribution endpoint"""
        return self.fetch_identifier_component("block/rental_value_distribution", block_data)

    def value_distribution(self, block_data):
        """Call the value_distribution endpoint"""
        return self.fetch_identifier_component("block/value_distribution", block_data)

    def value_ts(self, block_data):
        """Call the value_ts endpoint"""
        return self.fetch_identifier_component("block/value_ts", block_data)

    def value_ts_forecast(self, block_data):
        """Call the value_ts_forecast endpoint"""
        return self.fetch_identifier_component("block/value_ts_forecast", block_data)

    def value_ts_historical(self, block_data):
        """Call the value_ts_historical endpoint"""
        return self.fetch_identifier_component("block/value_ts_historical", block_data)

    def component_mget(self, block_data, components):
        """Call the block component_mget endpoint

        Args:
            - block_data - As described in the class docstring.
            - components - A list of strings for each component to include in the request.
                Example: ["block/value_ts", "block/value_distribution"]
        """
        if not isinstance(components, list):
            print("Components param must be a list")
            return

        query_params = {"components": ",".join(components)}

        return self.fetch_identifier_component(
            "block/component_mget", block_data, query_params)


class ZipComponentWrapper(ComponentWrapper):
    """Zip specific components

    All of the Analytics API zip endpoints take a ``zip_data`` argument.
    zip_data can be in the following forms:

    - A dict with a ``zipcode`` like:
      {"zipcode": "90274", "meta": "someId"}

    - A list of dicts as specified above:
      [{"zipcode": "90274", "meta": "someId"}, {"zipcode": "01960", "meta": "someId2}]

    - A single string representing a ``zipcode``:
      "90274"

    - A list of ``zipcode`` strings:
      ["90274", "01960"]

    The "meta" field is always optional.

    All of the zip endpoint methods return a ZipResponse,
    or the output of a custom OutputGenerator if one was specified in the constructor.
    """

    def _convert_to_identifier_json(self, zip_data):
        if isinstance(zip_data, str):
            # allow just passing a zipcode string.
            return {"zipcode": zip_data}

        if isinstance(zip_data, dict):
            allowed_keys = ["zipcode", "meta"]

            # ensure the dict does not contain any unallowed keys
            for key in zip_data:
                if key not in allowed_keys:
                    msg = "Key in zip input not allowed: " + key
                    raise housecanary.exceptions.InvalidInputException(msg)

            # ensure it contains a "zipcode" key
            if "zipcode" in zip_data:
                return zip_data

        # if we made it here, the input was not valid.
        msg = ("Input is invalid. Must be a dict or list of dicts"
               " with each item containing at least 'zipcode' key.")
        raise housecanary.exceptions.InvalidInputException((msg))

    def details(self, zip_data):
        """Call the details endpoint"""
        return self.fetch_identifier_component("zip/details", zip_data)

    def hpi_forecast(self, zip_data):
        """Call the hpi_forecast endpoint"""
        return self.fetch_identifier_component("zip/hpi_forecast", zip_data)

    def hpi_historical(self, zip_data):
        """Call the hpi_historical endpoint"""
        return self.fetch_identifier_component("zip/hpi_historical", zip_data)

    def hpi_ts(self, zip_data):
        """Call the hpi_ts endpoint"""
        return self.fetch_identifier_component("zip/hpi_ts", zip_data)

    def hpi_ts_forecast(self, zip_data):
        """Call the hpi_ts_forecast endpoint"""
        return self.fetch_identifier_component("zip/hpi_ts_forecast", zip_data)

    def hpi_ts_historical(self, zip_data):
        """Call the hpi_ts_historical endpoint"""
        return self.fetch_identifier_component("zip/hpi_ts_historical", zip_data)

    def volatility(self, zip_data):
        """Call the volatility endpoint"""
        return self.fetch_identifier_component("zip/volatility", zip_data)

    def component_mget(self, zip_data, components):
        """Call the zip component_mget endpoint

        Args:
            - zip_data - As described in the class docstring.
            - components - A list of strings for each component to include in the request.
                Example: ["zip/details", "zip/volatility"]
        """
        if not isinstance(components, list):
            print("Components param must be a list")
            return

        query_params = {"components": ",".join(components)}

        return self.fetch_identifier_component(
            "zip/component_mget", zip_data, query_params)


class MsaComponentWrapper(ComponentWrapper):
    """MSA specific components

    All of the Analytics API msa endpoints take an ``msa_data`` argument.
    msa_data can be in the following forms:

    - A dict with an ``msa`` like:
      {"msa": "41860", "meta": "someId"}

    - A list of dicts as specified above:
      [{"msa": "41860", "meta": "someId"}, {"msa": "40928", "meta": "someId2}]

    - A single string representing a ``msa``:
      "41860"

    - A list of ``msa`` strings:
      ["41860", "40928"]

    The "meta" field is always optional.

    All of the msa endpoint methods return an MsaResponse,
    or the output of a custom OutputGenerator if one was specified in the constructor.
    """

    def _convert_to_identifier_json(self, msa_data):
        if isinstance(msa_data, str):
            # allow just passing a msa string.
            return {"msa": msa_data}

        if isinstance(msa_data, dict):
            allowed_keys = ["msa", "meta"]

            # ensure the dict does not contain any unallowed keys
            for key in msa_data:
                if key not in allowed_keys:
                    msg = "Key in msa input not allowed: " + key
                    raise housecanary.exceptions.InvalidInputException(msg)

            # ensure it contains a "msa" key
            if "msa" in msa_data:
                return msa_data

        # if we made it here, the input was not valid.
        msg = ("Input is invalid. Must be a dict or list of dicts"
               " with each item containing at least 'msa' key.")
        raise housecanary.exceptions.InvalidInputException((msg))

    def details(self, msa_data):
        """Call the details endpoint"""
        return self.fetch_identifier_component("msa/details", msa_data)

    def hpi_ts(self, msa_data):
        """Call the hpi_ts endpoint"""
        return self.fetch_identifier_component("msa/hpi_ts", msa_data)

    def hpi_ts_forecast(self, msa_data):
        """Call the hpi_ts_forecast endpoint"""
        return self.fetch_identifier_component("msa/hpi_ts_forecast", msa_data)

    def hpi_ts_historical(self, msa_data):
        """Call the hpi_ts_historical endpoint"""
        return self.fetch_identifier_component("msa/hpi_ts_historical", msa_data)

    def component_mget(self, msa_data, components):
        """Call the msa component_mget endpoint

        Args:
            - msa_data - As described in the class docstring.
            - components - A list of strings for each component to include in the request.
                Example: ["msa/details", "msa/hpi_ts"]
        """
        if not isinstance(components, list):
            print("Components param must be a list")
            return

        query_params = {"components": ",".join(components)}

        return self.fetch_identifier_component(
            "msa/component_mget", msa_data, query_params)
