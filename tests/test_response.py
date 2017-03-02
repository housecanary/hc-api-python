"""
These tests require the HC_API_KEY and HC_API_SECRET environment variables to be set.
"""

# pylint: disable=missing-docstring

import unittest
from housecanary.apiclient import ApiClient
from housecanary.object import Property
from housecanary.object import Block
from housecanary.object import ZipCode


class PropertyResponseTestCase(unittest.TestCase):
    def setUp(self):
        self.client = ApiClient()
        self.test_data = [{"address": "43 Valmonte Plaza", "zipcode": "90274"}]

    def test_endpoint_name(self):
        response = self.client.fetch("property/value", self.test_data)
        self.assertEqual(response.endpoint_name, "property/value")

    def test_json(self):
        response = self.client.fetch("property/value", self.test_data)
        self.assertTrue(isinstance(response.json(), list))

    def test_response(self):
        response = self.client.fetch("property/value", self.test_data)
        self.assertIsNotNone(response.response)

    def test_get_object_errors(self):
        response = self.client.fetch("property/value", self.test_data)
        self.assertEqual(response.get_object_errors(), [])

    def test_get_object_errors_with_error(self):
        self.test_data[0]["zipcode"] = "00000"
        response = self.client.fetch("property/value", self.test_data)
        self.assertEqual(len(response.get_object_errors()), 1)

    def test_has_object_error(self):
        response = self.client.fetch("property/value", self.test_data)
        self.assertFalse(response.has_object_error())

    def test_has_object_error_with_error(self):
        self.test_data[0]["zipcode"] = "00000"
        response = self.client.fetch("property/value", self.test_data)
        self.assertTrue(response.has_object_error())

    def test_properties(self):
        response = self.client.fetch("property/value", self.test_data)
        self.assertTrue(len(response.properties()), 1)
        self.assertTrue(isinstance(response.properties()[0], Property))

    def test_properties_with_multiple(self):
        self.test_data.append({"address": "85 Clay St", "zipcode": "02140"})
        response = self.client.fetch("property/value", self.test_data)
        self.assertTrue(len(response.properties()), 2)
        self.assertTrue(isinstance(response.properties()[0], Property))
        self.assertTrue(isinstance(response.properties()[1], Property))

    def test_response_rate_limits(self):
        response = self.client.fetch("property/value", self.test_data)
        self.assertTrue(isinstance(response.rate_limits, list))
        self.assertTrue(isinstance(response.rate_limits[0]['period'], str))


class BlockResponseTestCase(unittest.TestCase):
    def setUp(self):
        self.client = ApiClient()
        self.test_data = [{"block_id": "060376703241005"}]

    def test_blocks(self):
        response = self.client.fetch("block/value_ts", self.test_data)
        self.assertTrue(len(response.blocks()), 1)
        self.assertTrue(isinstance(response.blocks()[0], Block))

    def test_blocks_with_multiple(self):
        self.test_data.append({"block_id": "160376703241005"})
        response = self.client.fetch("block/value_ts", self.test_data)
        self.assertTrue(len(response.blocks()), 2)
        self.assertTrue(isinstance(response.blocks()[0], Block))
        self.assertTrue(isinstance(response.blocks()[1], Block))


class ZipCodeResponseTestCase(unittest.TestCase):
    def setUp(self):
        self.client = ApiClient()
        self.test_data = [{"zipcode": "90274"}]

    def test_zipcodes(self):
        response = self.client.fetch("zip/details", self.test_data)
        self.assertTrue(len(response.zipcodes()), 1)
        self.assertTrue(isinstance(response.zipcodes()[0], ZipCode))

    def test_zipcodes_with_multiple(self):
        self.test_data.append({"zipcode": "01960"})
        response = self.client.fetch("zip/details", self.test_data)
        self.assertTrue(len(response.zipcodes()), 2)
        self.assertTrue(isinstance(response.zipcodes()[0], ZipCode))
        self.assertTrue(isinstance(response.zipcodes()[1], ZipCode))


if __name__ == "__main__":
    unittest.main()
