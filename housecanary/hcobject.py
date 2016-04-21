"""
housecanary.hcobject

This module provides a HouseCanaryObject class which encapsulates
an object and its associated data from the HouseCanary API.
Currently, only the HouseCanaryProperty subclass is implemented.
"""

import housecanary.constants as hcconstants

class HouseCanaryObject(object):
    """Base class that for various types of objects returned from the HouseCanary API."""

    def __init__(self, data, api_code, api_code_description):
        """Constructor

        Args:
            data - Json data returned from the API for this object.
            api_code - The HouseCanary business logic error code.
            api_code_description - The HouseCanary business logic error description.
        """
        self.api_code = api_code
        self.api_code_description = api_code_description
        self.json_results = data

    def has_error(self):
        """Returns whether there was a business logic error fetching data
        for this property.

        Returns:
            boolean
        """
        return self.api_code > hcconstants.HC_BIZ_CODE_OK

    def get_error(self):
        """If there was a business error fetching data for this property,
        returns the error message.

        Returns:
            string - the error message, or None if there was no error.

        """
        return self.api_code_description

    def __str__(self):
        return "HouseCanaryObject"

class HouseCanaryProperty(HouseCanaryObject):
    """Encapsulate the representation of a single address"""

    def __init__(self, address=None, zipcode=None, data=None, 
                 api_code=0, api_code_description=None):
        """Initialize the HouseCanaryProperty object

        Args:
            address (required) -- Building number, street name and unit number.
            zipcode (required) -- Zipcode that matches the address.
            data (optional) -- The data returned from the API for this property.
            api_code (optional) -- The HouseCanary business logic
                error code reflecting any error with this property.
            api_code_description (optional) -- The HouseCanary business logic 
                error description.
        """
        super(HouseCanaryProperty, self).__init__(data, api_code, api_code_description)
        
        self.address = str(address)
        self.zipcode = str(zipcode)
        self.zipcode_plus4 = None
        self.address_full = None
        self.city = None
        self.county_fips = None
        self.lat = None
        self.lng = None
        self.state = None
        self.unit = None
        self.meta = None

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
        hc_property.unit = address_info["unit"]

        hc_property.meta = None
        if "meta" in json_data:
            hc_property.meta = json_data["meta"]

        endpoint_data = json_data[endpoint_name]
        hc_property.api_code = endpoint_data["api_code"]
        hc_property.api_code_description = endpoint_data["api_code_description"]
        hc_property.json_results = endpoint_data["result"]

        return hc_property

    def __str__(self):
        return self.address

class HouseCanaryZipcode(HouseCanaryObject):
    pass

class HouseCanaryLatLng(HouseCanaryObject):
    pass
