"""
housecanary.hcproperty

This module provides a HouseCanaryProperty class which encapsulates
an address and its associated data from the HouseCanary API.
"""

import uuid

HC_BIZ_CODE_OK = 0

class HouseCanaryProperty(object):
    """Encapsulate the representation of a single address"""

    def __init__(self, address=None, zipcode=None, data=None, api_code=0):
        """Initialize the HouseCanaryProperty object

        Args:
            address (required) -- Building number, street name and unit number.
            zipcode (required) -- Zipcode that matches the address.
            data (optional) -- The data returned from the API for this property.
            api_code (optional) -- The HouseCanary business logic
                error code reflecting any error with this property.
        """

        self.address = str(address)
        self.zipcode = str(zipcode)
        self.json_results = data
        self.api_code = int(api_code)

    @classmethod
    def create_from_json(cls, endpoint_name, json_data):
        """Deserialize property json data into a HouseCanaryProperty object

        Args:
            json_data (dict): The json data for this property

        Returns:
            HouseCanaryProperty object

        """        
        hc_property = HouseCanaryProperty()
        address_info = json_data["address_info"]
        hc_property.address = address_info["address"]
        hc_property.zipcode = address_info["zipcode"]
        hc_property.zipcode_plus4 = address_info["zipcode_plus4"]
        hc_property.address_full = address_info["address_full"]
        hc_property.city = address_info["city"]
        hc_property.county_fips = address_info["county_fips"]
        hc_property.lat = address_info["lat"]
        hc_property.lng = address_info["lng"]
        hc_property.state = address_info["state"]
        hc_property.unit = address_info["city"]

        hc_property.meta = None
        if "meta" in json_data:
            hc_property.meta = json_data["meta"]

        endpoint_data = json_data[endpoint_name]
        hc_property.api_code = endpoint_data["api_code"]
        hc_property.api_code_description = endpoint_data["api_code_description"]
        hc_property.json_results = endpoint_data["result"]

        return hc_property

    def has_property_error(self):
        """Returns whether there was a business logic error fetching data
        for this property.

        Returns:
            boolean
        """
        return self.api_code > HC_BIZ_CODE_OK

    def get_property_error(self):
        """If there was a business error fetching data for this property,
        returns the error message.

        Returns:
            string - the error message, or None if there was no error.

        """
        return self.api_code_description
