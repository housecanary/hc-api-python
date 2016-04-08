import uuid

HC_BIZ_CODE_OK = 0

class HouseCanaryProperty(object):
    """Encapsulate the representation of a single address"""

    def __init__(self, address, zipcode, unique_id="", data=None, hc_business_error_code=0):
        """Initialize the HouseCanaryProperty object

        Args:
            address (required) -- Building number, street name and unit number.
            zipcode (required) -- Zipcode that matches the address.
            unique_id (optional) -- A string used in the response from
                API calls to reference this address.
                If not specified, unique_id is randomly generated.
            data (optional) -- The data returned from the API for this property.
                Omit this if you are using this object to call the API.
            hc_business_error_code (optional) -- The HouseCanary business logic
                error code reflecting any error with this property.
                Omit this if you are using this object to call the API.
        """

        self.address = str(address)
        self.zipcode = str(zipcode)
        self.unique_id = str(unique_id) or str(uuid.uuid4())
        self.data = data
        self.hc_business_error_code = int(hc_business_error_code)

    @classmethod
    def create_from_json(cls, unique_id, json_data):
        """Deserialize property json data into a HouseCanaryProperty object

        Args:
            unique_id (str): The unique_id associated with this property
            json_data (dict): The json data for this property

        Returns:
            HouseCanaryProperty object

        """
        address = None
        zipcode = None
        code = HC_BIZ_CODE_OK
        if "address" in json_data:
            if "address" in json_data["address"]:
                address = json_data["address"]["address"]
            if "zipcode" in json_data["address"]:
                zipcode = json_data["address"]["zipcode"]
        if "code" in json_data:
            code = json_data["code"]

        return cls(address, zipcode, unique_id, json_data, code)

    def has_business_error(self):
        """Returns whether there was a business logic error fetching data
        for this property.

        Returns:
            boolean
        """
        return self.hc_business_error_code > HC_BIZ_CODE_OK

    def get_business_error(self):
        """If there was a business error fetching data for this property,
        returns the error message.

        Returns:
            string - the error message, or None if there was no error.

        """
        if not self.has_business_error():
            return None
        else:
            if "code_description" in self.data:
                return self.data["code_description"]
            else:
                return None
