"""
These tests require the HC_API_KEY and HC_API_SECRET environment variables to be set.
"""

# pylint: disable=missing-docstring

import unittest
from housecanary.hcapiclient import ApiClient
from housecanary.hcproperty import HouseCanaryProperty

class HouseCanaryResponseTestCase(unittest.TestCase):
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

    def test_get_property_errors(self):
        response = self.client.fetch("property/score", self.test_data)
        self.assertEqual(response.get_property_errors(), [])

    def test_get_property_errors_with_error(self):
        self.test_data[0]["zipcode"] = "00000"
        response = self.client.fetch("property/score", self.test_data)
        self.assertEqual(len(response.get_property_errors()), 1)

    def test_has_property_error(self):
        response = self.client.fetch("property/score", self.test_data)
        self.assertFalse(response.has_property_error())

    def test_has_property_error_with_error(self):
        self.test_data[0]["zipcode"] = "00000"
        response = self.client.fetch("property/score", self.test_data)
        self.assertTrue(response.has_property_error())

    def test_hc_properties(self):
        response = self.client.fetch("property/score", self.test_data)
        self.assertTrue(len(response.hc_properties()), 1)
        self.assertTrue(isinstance(response.hc_properties()[0], HouseCanaryProperty))

    def test_hc_properties_with_multiple(self):
        self.test_data.append({"address": "85 Clay St", "zipcode": "02140"})
        response = self.client.fetch("property/score", self.test_data)
        self.assertTrue(len(response.hc_properties()), 2)
        self.assertTrue(isinstance(response.hc_properties()[0], HouseCanaryProperty))
        self.assertTrue(isinstance(response.hc_properties()[1], HouseCanaryProperty))

if __name__ == "__main__":
    unittest.main()
