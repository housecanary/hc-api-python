"""
Provides a HouseCanaryObject class which encapsulates
an object and its associated data.
Currently, only the Property subclass is implemented.
"""

import housecanary.constants as constants


class HouseCanaryObject(object):
    """Base class for returned API objects."""

    def __init__(self):
        """
        Args:
            data - Json data returned from the API for this object.
            api_code - The HouseCanary business logic error code.
            api_code_description - The HouseCanary business logic error description.
        """
        self.component_results = []

    def has_error(self):
        """Returns whether there was a business logic error when fetching data
        for any components for this property.

        Returns:
            boolean
        """
        return next(
            (True for cr in self.component_results
             if cr.has_error()),
            False
        )

    def get_errors(self):
        """If there were any business errors fetching data for this property,
        returns the error messages.

        Returns:
            string - the error message, or None if there was no error.

        """
        return [{cr.component_name: cr.get_error()}
                for cr in self.component_results if cr.has_error()]

    def __str__(self):
        return "HouseCanaryObject"


class Property(HouseCanaryObject):
    """A single address"""

    def __init__(self, address=None, zipcode=None):
        """
        Args:
            address (required) -- Building number, street name and unit number.
            zipcode (required) -- Zipcode that matches the address.
            data (optional) -- The data returned from the API for this property.
            api_code (optional) -- The HouseCanary business logic
                error code reflecting any error with this property.
            api_code_description (optional) -- The HouseCanary business logic
                error description.
        """
        super(Property, self).__init__()

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
    def create_from_json(cls, json_data):
        """Deserialize property json data into a Property object

        Args:
            json_data (dict): The json data for this property

        Returns:
            Property object

        """
        prop = Property()
        address_info = json_data["address_info"]
        prop.address = address_info["address"]
        prop.zipcode = address_info["zipcode"]
        prop.zipcode_plus4 = address_info["zipcode_plus4"]
        prop.address_full = address_info["address_full"]
        prop.city = address_info["city"]
        prop.county_fips = address_info["county_fips"]
        prop.lat = address_info["lat"]
        prop.lng = address_info["lng"]
        prop.state = address_info["state"]
        prop.unit = address_info["unit"]

        prop.meta = None
        if "meta" in json_data:
            prop.meta = json_data["meta"]

        # create a ComponentResult from each returned component's data
        # and append to this property's component_results list.
        for key, value in json_data.iteritems():
            if key not in ["address_info", "meta"]:
                component_result = ComponentResult(
                    key,
                    value["result"],
                    value["api_code"],
                    value["api_code_description"]
                )

                prop.component_results.append(component_result)

        return prop

    def __str__(self):
        return self.address


class Zipcode(HouseCanaryObject):
    pass


class LatLng(HouseCanaryObject):
    pass


class ComponentResult(object):
    """The results of a single component"""

    def __init__(self, component_name, json_data, api_code, api_code_description):
        """
        Args:
            component_name - string name of the component.
            json_data - Json data returned from the API for this object.
            api_code - The HouseCanary business logic error code.
            api_code_description - The HouseCanary business logic error description.
        """
        self.component_name = component_name
        self.json_data = json_data
        self.api_code = api_code
        self.api_code_description = api_code_description

    def has_error(self):
        """Returns whether this component had a business logic error"""
        return self.api_code > constants.BIZ_CODE_OK

    def get_error(self):
        """Gets the error of this component, if any"""
        return self.api_code_description
