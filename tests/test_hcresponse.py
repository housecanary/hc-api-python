"""
These tests require the HC_API_KEY and HC_API_SECRET environment variables to be set.
"""

# pylint: disable=missing-docstring

import unittest
from housecanary.hcapiclient import ApiClient
from housecanary.hcobject import HouseCanaryAddress

class HouseCanaryAddressResponseTestCase(unittest.TestCase):
    def setUp(self):
        self.client = ApiClient()
        self.test_data = [{"address":"47 Perley Ave", "zipcode":"01960"}]

    def test_endpoint_name(self):
        response = self.client.fetch("property/score", self.test_data)
        self.assertEqual(response.endpoint_name, "property/score")

    def test_json(self):
        response = self.client.fetch("property/score", self.test_data)
        self.assertTrue(isinstance(response.json(), list))

    def test_response(self):
        response = self.client.fetch("property/score", self.test_data)
        self.assertIsNotNone(response.response)

    def test_get_object_errors(self):
        response = self.client.fetch("property/score", self.test_data)
        self.assertEqual(response.get_object_errors(), [])

    def test_get_object_errors_with_error(self):
        self.test_data[0]["zipcode"] = "00000"
        response = self.client.fetch("property/score", self.test_data)
        self.assertEqual(len(response.get_object_errors()), 1)

    def test_has_object_error(self):
        response = self.client.fetch("property/score", self.test_data)
        self.assertFalse(response.has_object_error())

    def test_has_object_error_with_error(self):
        self.test_data[0]["zipcode"] = "00000"
        response = self.client.fetch("property/score", self.test_data)
        self.assertTrue(response.has_object_error())

    def test_hc_addresses(self):
        response = self.client.fetch("property/score", self.test_data)
        self.assertTrue(len(response.hc_addresses()), 1)
        self.assertTrue(isinstance(response.hc_addresses()[0], HouseCanaryAddress))

    def test_hc_addresses_with_multiple(self):
        self.test_data.append({"address": "85 Clay St", "zipcode": "02140"})
        response = self.client.fetch("property/score", self.test_data)
        self.assertTrue(len(response.hc_addresses()), 2)
        self.assertTrue(isinstance(response.hc_addresses()[0], HouseCanaryAddress))
        self.assertTrue(isinstance(response.hc_addresses()[1], HouseCanaryAddress))

if __name__ == "__main__":
    unittest.main()
