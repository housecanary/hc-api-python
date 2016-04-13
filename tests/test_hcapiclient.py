"""
These tests require the HC_API_KEY and HC_API_SECRET environment variables to be set.
"""
# pylint: disable=missing-docstring

import unittest
import mock
from housecanary.hcapiclient import ApiClient, PropertyApiClient
from housecanary.hcresponse import HouseCanaryResponse
from housecanary.output import JsonOutputGenerator

class ApiClientTestCase(unittest.TestCase):
    """Tests for the ApiClient class"""

    def test_fetch(self):
        client = ApiClient()
        post_data = [{"address":"47 Perley Ave", "zipcode":"01960"}]
        response = client.fetch("property/score", post_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))

    def test_fetch_with_tuples(self):
        client = ApiClient()
        post_data = [("47 Perley Ave", "01960"), ("85 Clay St", "01960")]
        response = client.fetch("property/score", post_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))

    def test_fetch_with_single_tuple(self):
        client = ApiClient()
        post_data = ("47 Perley Ave", "01960")
        response = client.fetch("property/score", post_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))

    def test_fetch_with_custom_request_client(self):
        custom_request_client = mock.MagicMock()
        custom_request_client.post.return_value = "Response body"
        client = ApiClient(request_client=custom_request_client)
        post_data = [{"address":"47 Perley Ave", "zipcode":"01960"}]
        response = client.fetch("property/score", post_data)
        self.assertEqual(response, "Response body")

    def test_fetch_with_custom_ouput_generator(self):
        custom_output_generator = mock.MagicMock()
        custom_output_generator.process_response.return_value = "Custom Response"
        client = ApiClient(output_generator=custom_output_generator)
        post_data = [{"address":"47 Perley Ave", "zipcode":"01960"}]
        response = client.fetch("property/score", post_data)
        self.assertEqual(response, "Custom Response")

    def test_fetch_with_json_output_generator(self):
        output_generator = JsonOutputGenerator()
        client = ApiClient(output_generator=output_generator)
        post_data = [{"address":"47 Perley Ave", "zipcode":"01960"}]
        response = client.fetch("property/score", post_data)
        self.assertTrue(isinstance(response, list))

    def test_fetch_with_custom_auth(self):
        auth = mock.MagicMock()
        auth.process.return_value = "Auth Processed"
        class TestRequestClient(object):
            def __init__(self, output_generator, authenticator):
                self._output_generator = output_generator
                self._auth = authenticator
            def post(self, url, post_data):
                return self._auth.process()

        request_client = TestRequestClient(None, auth)
        client = ApiClient(request_client=request_client)
        post_data = [{"address":"47 Perley Ave", "zipcode":"01960"}]
        response = client.fetch("property/score", post_data)
        self.assertEqual(response, "Auth Processed")


class PropertyApiClientTestCase(unittest.TestCase):
    """Tests for the PropertyApiClient class."""

    def setUp(self):
        self.client = PropertyApiClient()
        self.test_data = [{"address":"47 Perley Ave", "zipcode":"01960"}]

    def test_flood(self):
        response = self.client.flood(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/flood"])

    def test_school(self):
        response = self.client.school(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/school"])

    def test_value(self):
        response = self.client.value(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/value"])

    def test_value_forecast(self):
        response = self.client.value_forecast(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/value_forecast"])

    def test_score(self):
        response = self.client.score(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/score"])

    def test_zip_hpi_historical(self):
        response = self.client.zip_hpi_historical(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/zip_hpi_historical"])

    def test_zip_hpi_forecast(self):
        response = self.client.zip_hpi_forecast(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/zip_hpi_forecast"])

    def test_rental_value(self):
        response = self.client.rental_value(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/rental_value"])

    def test_msa_details(self):
        response = self.client.msa_details(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/msa_details"])

    def test_mortgage_lien(self):
        response = self.client.mortgage_lien(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/mortgage_lien"])

    def test_ltv(self):
        response = self.client.ltv(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/ltv"])

    def test_ltv_forecast(self):
        response = self.client.ltv_forecast(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/ltv_forecast"])

    def test_owner_occupied(self):
        response = self.client.owner_occupied(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/owner_occupied"])

    def test_details(self):
        response = self.client.details(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/details"])

    def test_sales_history(self):
        response = self.client.sales_history(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/sales_history"])

    def test_mls(self):
        response = self.client.mls(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/mls"])

    def test_nod(self):
        response = self.client.nod(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/nod"])

    def test_census(self):
        response = self.client.census(self.test_data)
        self.assertTrue(isinstance(response, HouseCanaryResponse))
        self.assertIsNotNone(response.json_body[0]["property/census"])

if __name__ == "__main__":
    unittest.main()
