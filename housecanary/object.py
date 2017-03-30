"""
Provides a HouseCanaryObject class which encapsulates
an object and its associated data.
Currently, only the Property subclass is implemented.
"""

from builtins import str
from builtins import next
from builtins import object
import housecanary.constants as constants


def _create_component_results(json_data, result_key):
    """ Returns a list of ComponentResult from the json_data"""
    component_results = []
    for key, value in list(json_data.items()):
        if key not in [result_key, "meta"]:
            component_result = ComponentResult(
                key,
                value["result"],
                value["api_code"],
                value["api_code_description"]
            )

            component_results.append(component_result)

    return component_results


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
        self.block_id = None
        self.zipcode_plus4 = None
        self.address_full = None
        self.city = None
        self.county_fips = None
        self.geo_precision = None
        self.lat = None
        self.lng = None
        self.slug = None
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
        prop.block_id = address_info["block_id"]
        prop.zipcode = address_info["zipcode"]
        prop.zipcode_plus4 = address_info["zipcode_plus4"]
        prop.address_full = address_info["address_full"]
        prop.city = address_info["city"]
        prop.county_fips = address_info["county_fips"]
        prop.geo_precision = address_info["geo_precision"]
        prop.lat = address_info["lat"]
        prop.lng = address_info["lng"]
        prop.slug = address_info["slug"]
        prop.state = address_info["state"]
        prop.unit = address_info["unit"]

        prop.meta = None
        if "meta" in json_data:
            prop.meta = json_data["meta"]

        prop.component_results = _create_component_results(json_data, "address_info")

        return prop

    def __str__(self):
        return self.address or self.meta or "PropertyObject"


class Block(HouseCanaryObject):
    """A single block"""

    def __init__(self, block_id=None):
        """
        Args:
            block_id (required) -- Block ID.
            data (optional) -- The data returned from the API for this block.
            api_code (optional) -- The HouseCanary business logic
                error code reflecting any error with this block.
            api_code_description (optional) -- The HouseCanary business logic error description.
        """
        super(Block, self).__init__()

        self.block_id = str(block_id)
        self.num_bins = None
        self.property_type = None
        self.meta = None

    @classmethod
    def create_from_json(cls, json_data):
        """Deserialize block json data into a Block object

        Args:
            json_data (dict): The json data for this block

        Returns:
            Block object

        """
        block = Block()
        block_info = json_data["block_info"]
        block.block_id = block_info["block_id"]
        block.num_bins = block_info["num_bins"] if "num_bins" in block_info else None
        block.property_type = block_info["property_type"] if "property_type" in block_info else None
        block.meta = json_data["meta"] if "meta" in json_data else None

        block.component_results = _create_component_results(json_data, "block_info")

        return block

    def __str__(self):
        return self.block_id or self.meta or "BlockObject"


class ZipCode(HouseCanaryObject):
    """A single zipcode"""

    def __init__(self, zipcode=None):
        """
        Args:
            zipcode (required) -- Zipcode.
            data (optional) -- The data returned from the API for this zipcode.
            api_code (optional) -- The HouseCanary business logic
                error code reflecting any error with this zipcode.
            api_code_description (optional) -- The HouseCanary business logic error description.
        """
        super(ZipCode, self).__init__()

        self.zipcode = str(zipcode)
        self.meta = None

    @classmethod
    def create_from_json(cls, json_data):
        """Deserialize zipcode json data into a ZipCode object

        Args:
            json_data (dict): The json data for this zipcode

        Returns:
            Zip object

        """
        zipcode = ZipCode()
        zipcode.zipcode = json_data["zipcode_info"]["zipcode"]
        zipcode.meta = json_data["meta"] if "meta" in json_data else None

        zipcode.component_results = _create_component_results(json_data, "zipcode_info")

        return zipcode

    def __str__(self):
        return self.zipcode or self.meta or "ZipCodeObject"


class Msa(HouseCanaryObject):
    """A single MSA"""

    def __init__(self, msa=None):
        """
        Args:
            msa (required) -- MSA.
            data (optional) -- The data returned from the API for this MSA.
            api_code (optional) -- The HouseCanary business logic
                error code reflecting any error with this MSA.
            api_code_description (optional) -- The HouseCanary business logic error description.
        """
        super(Msa, self).__init__()

        self.msa = str(msa)
        self.meta = None

    @classmethod
    def create_from_json(cls, json_data):
        """Deserialize msa json data into a Msa object

        Args:
            json_data (dict): The json data for this msa

        Returns:
            Msa object

        """
        msa = Msa()
        msa.msa = json_data["msa_info"]["msa"]
        msa.meta = json_data["meta"] if "meta" in json_data else None

        msa.component_results = _create_component_results(json_data, "msa_info")

        return msa

    def __str__(self):
        return self.msa or self.meta or "MsaObject"


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
