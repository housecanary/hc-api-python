"""
These tests require the HC_API_KEY and HC_API_SECRET environment variables to be set.
"""
# pylint: disable=missing-docstring

import unittest
import mock
from housecanary.apiclient import ApiClient
from housecanary.response import PropertyResponse
from housecanary.output import JsonOutputGenerator
import housecanary.constants as constants
import housecanary.exceptions


class ApiClientTestCase(unittest.TestCase):
    """Tests for the ApiClient class"""

    def test_fetch(self):
        client = ApiClient()
        client._request_client.get = mock.MagicMock()
        post_data = [{"address": "47 Perley Ave", "zipcode": "01960"}]

        client.fetch("property/value", post_data)

        expected_url = constants.URL_PREFIX + "/v2/property/value"
        client._request_client.get.assert_called_with(expected_url, post_data[0])

    def test_fetch_with_custom_request_client(self):
        custom_request_client = mock.MagicMock()
        custom_request_client.get.return_value = "Response body"
        client = ApiClient(request_client=custom_request_client)
        post_data = [{"address": "47 Perley Ave", "zipcode": "01960"}]
        response = client.fetch("property/value", post_data)
        self.assertEqual(response, "Response body")

    def test_fetch_with_custom_ouput_generator(self):
        custom_output_generator = mock.MagicMock()
        custom_output_generator.process_response.return_value = "Custom Response"
        client = ApiClient(output_generator=custom_output_generator)
        post_data = [{"address": "47 Perley Ave", "zipcode": "01960"}]
        response = client.fetch("property/value", post_data)
        self.assertEqual(response, "Custom Response")

    def test_fetch_with_json_output_generator(self):
        output_generator = JsonOutputGenerator()
        client = ApiClient(output_generator=output_generator)
        post_data = [{"address": "47 Perley Ave", "zipcode": "01960"}]
        response = client.fetch("property/value", post_data)
        self.assertTrue(isinstance(response, list))

    def test_fetch_with_custom_auth(self):
        auth = mock.MagicMock()
        auth.process.return_value = "Auth Processed"

        class TestRequestClient(object):
            def __init__(self, output_generator, authenticator):
                self._output_generator = output_generator
                self._auth = authenticator

            def get(self, url, post_data, query_params=None):
                return self._auth.process()

        request_client = TestRequestClient(None, auth)
        client = ApiClient(request_client=request_client)
        post_data = [{"address": "47 Perley Ave", "zipcode": "01960"}]
        response = client.fetch("property/value", post_data)
        self.assertEqual(response, "Auth Processed")

    def test_fetch_synchronous(self):
        client = ApiClient()
        client._request_client.get = mock.MagicMock()

        client.fetch_synchronous("property/value")

        expected_url = constants.URL_PREFIX + "/v2/property/value"
        client._request_client.get.assert_called_with(expected_url, {})


class PropertyComponentWrapperTestCase(unittest.TestCase):
    """Tests for the PropertyComponentWrapper class."""

    def setUp(self):
        self.client = ApiClient()
        self.test_data = [{"address": "47 Perley Ave", "zipcode": "01960", "meta": "addr1"}]

    def test_get_property_input_with_single_tuple(self):
        address_data = ("47 Perley Ave", "01960")
        property_input = self.client.property.get_property_input(address_data)
        self.assertEqual(property_input, [{"address": "47 Perley Ave", "zipcode": "01960"}])

    def test_get_property_input_with_multiple_tuples(self):
        address_data = [("47 Perley Ave", "01960"), ("85 Clay St", "02140")]
        property_input = self.client.property.get_property_input(address_data)
        self.assertEqual(property_input, [{"address": "47 Perley Ave", "zipcode": "01960"},
                                          {"address": "85 Clay St", "zipcode": "02140"}])

    def test_get_property_input_with_slug_string(self):
        address_data = "123-Example-St-San-Francisco-CA-94105"
        property_input = self.client.property.get_property_input(address_data)
        self.assertEqual(property_input, [{"slug": "123-Example-St-San-Francisco-CA-94105"}])

    def test_get_property_input_with_invalid_key(self):
        address_data = [{"address": "47 Perley Ave", "zipcode": "01960", "color": "green"}]
        with self.assertRaises(housecanary.exceptions.InvalidInputException):
            self.client.property.get_property_input(address_data)

    def test_get_property_input_with_city_state_unit(self):
        address_data = [{"address": "47 Perley Ave", "unit": "2", "city": "Peabody", "state": "MA"}]
        property_input = self.client.property.get_property_input(address_data)
        self.assertEqual(property_input, address_data)

    def test_get_property_input_with_slug_list(self):
        address_data = [{"slug": "123-Example-St-San-Francisco-CA-94105"},
                        {"slug": "345-Example-St-San-Francisco-CA-94105"}]
        property_input = self.client.property.get_property_input(address_data)
        self.assertEqual(property_input, address_data)

    def test_get_property_input_with_slug_dict(self):
        address_data = {"slug": "123-Example-St-San-Francisco-CA-94105"}
        property_input = self.client.property.get_property_input(address_data)
        self.assertEqual(property_input, [address_data])

    def test_get_property_input_with_meta(self):
        address_data = [{"address": "47 Perley Ave", "zipcode": "01960", "meta": "addr1"}]
        property_input = self.client.property.get_property_input(address_data)
        self.assertEqual(property_input, address_data)

    def test_get_property_input_with_multiple_addresses(self):
        address_data = [{"address": "47 Perley Ave", "zipcode": "01960"},
                        {"address": "123 Main St", "zipcode": "01010"}]
        property_input = self.client.property.get_property_input(address_data)
        self.assertEqual(property_input, address_data)

    def test_get_property_input_with_single_dict(self):
        address_data = {"address": "47 Perley Ave", "zipcode": "01960"}
        property_input = self.client.property.get_property_input(address_data)
        self.assertEqual(property_input, [address_data])

    def test_get_property_input_dict_without_address_slug(self):
        address_data = {"state": "CA"}
        with self.assertRaises(housecanary.exceptions.InvalidInputException):
            self.client.property.get_property_input(address_data)

    def test_get_property_input_list_without_address_slug(self):
        address_data = [{"state": "CA"},
                        {"address" "43 Valmonte Plaza"}]
        with self.assertRaises(housecanary.exceptions.InvalidInputException):
            self.client.property.get_property_input(address_data)

    def test_census(self):
        response = self.client.property.census(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/census"])

    def test_details(self):
        response = self.client.property.details(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/details"])

    def test_flood(self):
        response = self.client.property.flood(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/flood"])

    def test_ltv(self):
        response = self.client.property.ltv(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/ltv"])

    def test_ltv_details(self):
        response = self.client.property.ltv_details(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/ltv_details"])

    def test_mortgage_lien(self):
        response = self.client.property.mortgage_lien(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/mortgage_lien"])

    def test_msa_details(self):
        response = self.client.property.msa_details(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/msa_details"])

    def test_nod(self):
        response = self.client.property.nod(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/nod"])

    def test_owner_occupied(self):
        response = self.client.property.owner_occupied(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/owner_occupied"])

    def test_rental_value(self):
        response = self.client.property.rental_value(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/rental_value"])

    def test_sales_history(self):
        response = self.client.property.sales_history(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/sales_history"])

    def test_school(self):
        response = self.client.property.school(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/school"])

    def test_value(self):
        response = self.client.property.value(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/value"])

    def test_value_forecast(self):
        response = self.client.property.value_forecast(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/value_forecast"])

    def test_zip_details(self):
        response = self.client.property.zip_details(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/zip_details"])

    def test_zip_hpi_forecast(self):
        response = self.client.property.zip_hpi_forecast(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/zip_hpi_forecast"])

    def test_zip_hpi_historical(self):
        response = self.client.property.zip_hpi_historical(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/zip_hpi_historical"])

    def test_zip_volatility(self):
        response = self.client.property.zip_volatility(self.test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/zip_volatility"])

    def test_component_mget(self):
        components = ["property/value", "property/census"]
        response = self.client.property.component_mget(self.test_data, components)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/value"])
        self.assertIsNotNone(response.json()[0]["property/census"])

    def test_value_report(self):
        self.client.fetch_synchronous = mock.MagicMock()

        self.client.property.value_report("47 Perley Ave", "01960")

        expected_params = {
            "report_type": "full",
            "format": "json",
            "address": "47 Perley Ave",
            "zipcode": "01960"
        }
        self.client.fetch_synchronous.assert_called_with("property/value_report", expected_params)

    def test_rental_report(self):
        self.client.fetch_synchronous = mock.MagicMock()

        self.client.property.rental_report("47 Perley Ave", "01960")

        expected_params = {
            "format": "json",
            "address": "47 Perley Ave",
            "zipcode": "01960"
        }
        self.client.fetch_synchronous.assert_called_with("property/rental_report", expected_params)

    def test_multiple_properties(self):
        test_data = [{"address": "47 Perley Ave", "zipcode": "01960", "meta": "addr1"},
                     {"address": "43 Valmonte Plaza", "zipcode": "90274", "meta": "addr2"}]
        response = self.client.property.value(test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/value"])
        self.assertIsNotNone(response.json()[1]["property/value"])

    def test_with_city_state(self):
        test_data = [{"address": "47 Perley Ave", "city": "Peabody", "state": "MA"}]
        response = self.client.property.value(test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/value"])


if __name__ == "__main__":
    unittest.main()
