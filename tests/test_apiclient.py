"""
These tests require the HC_API_KEY and HC_API_SECRET environment variables to be set.
"""
# pylint: disable=missing-docstring

import unittest
import mock
from housecanary.apiclient import ApiClient
from housecanary.response import PropertyResponse
from housecanary.response import BlockResponse
from housecanary.response import ZipCodeResponse
from housecanary.response import MsaResponse
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
        property_input = self.client.property.get_identifier_input(address_data)
        self.assertEqual(property_input, [{"address": "47 Perley Ave", "zipcode": "01960"}])

    def test_get_property_input_with_multiple_tuples(self):
        address_data = [("47 Perley Ave", "01960"), ("85 Clay St", "02140")]
        property_input = self.client.property.get_identifier_input(address_data)
        self.assertEqual(property_input, [{"address": "47 Perley Ave", "zipcode": "01960"},
                                          {"address": "85 Clay St", "zipcode": "02140"}])

    def test_get_property_input_with_slug_string(self):
        address_data = "123-Example-St-San-Francisco-CA-94105"
        property_input = self.client.property.get_identifier_input(address_data)
        self.assertEqual(property_input, [{"slug": "123-Example-St-San-Francisco-CA-94105"}])

    def test_get_property_input_with_invalid_key(self):
        address_data = [{"address": "47 Perley Ave", "zipcode": "01960", "color": "green"}]
        with self.assertRaises(housecanary.exceptions.InvalidInputException):
            self.client.property.get_identifier_input(address_data)

    def test_get_property_input_with_city_state_unit(self):
        address_data = [{"address": "47 Perley Ave", "unit": "2", "city": "Peabody", "state": "MA"}]
        property_input = self.client.property.get_identifier_input(address_data)
        self.assertEqual(property_input, address_data)

    def test_get_property_input_with_slug_list(self):
        address_data = [{"slug": "123-Example-St-San-Francisco-CA-94105"},
                        {"slug": "345-Example-St-San-Francisco-CA-94105"}]
        property_input = self.client.property.get_identifier_input(address_data)
        self.assertEqual(property_input, address_data)

    def test_get_property_input_with_slug_dict(self):
        address_data = {"slug": "123-Example-St-San-Francisco-CA-94105"}
        property_input = self.client.property.get_identifier_input(address_data)
        self.assertEqual(property_input, [address_data])

    def test_get_property_input_with_meta(self):
        address_data = [{"address": "47 Perley Ave", "zipcode": "01960", "meta": "addr1"}]
        property_input = self.client.property.get_identifier_input(address_data)
        self.assertEqual(property_input, address_data)

    def test_get_property_input_with_multiple_addresses(self):
        address_data = [{"address": "47 Perley Ave", "zipcode": "01960"},
                        {"address": "123 Main St", "zipcode": "01010"}]
        property_input = self.client.property.get_identifier_input(address_data)
        self.assertEqual(property_input, address_data)

    def test_get_property_input_with_single_dict(self):
        address_data = {"address": "47 Perley Ave", "zipcode": "01960"}
        property_input = self.client.property.get_identifier_input(address_data)
        self.assertEqual(property_input, [address_data])

    def test_get_property_input_dict_without_address_slug(self):
        address_data = {"state": "CA"}
        with self.assertRaises(housecanary.exceptions.InvalidInputException):
            self.client.property.get_identifier_input(address_data)

    def test_get_property_input_list_without_address_slug(self):
        address_data = [{"state": "CA"},
                        {"address" "43 Valmonte Plaza"}]
        with self.assertRaises(housecanary.exceptions.InvalidInputException):
            self.client.property.get_identifier_input(address_data)

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

    def test_rental_value_within_block(self):
        test_data = [{"address": "47 Perley Ave", "zipcode": "01960", "meta": "addr1",
                      "client_value": 1000000, "client_value_sqft": 3000}]
        response = self.client.property.rental_value_within_block(test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/rental_value_within_block"])

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

    def test_value_within_block(self):
        test_data = [{"address": "47 Perley Ave", "zipcode": "01960", "meta": "addr1",
                      "client_value": 1000000, "client_value_sqft": 3000}]
        response = self.client.property.value_within_block(test_data)
        self.assertTrue(isinstance(response, PropertyResponse))
        self.assertIsNotNone(response.json()[0]["property/value_within_block"])

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


class BlockComponentWrapperTestCase(unittest.TestCase):
    """Tests for the BlockComponentWrapper class."""

    def setUp(self):
        self.client = ApiClient()
        self.test_data_num_bins = [{"block_id": "060750615003005", "num_bins": "5",
                                    "meta": "block1"}]
        self.test_data_prop_type = [{"block_id": "060750615003005", "meta": "block1",
                                     "property_type": "SFD"}]

    def test_get_block_input_with_single_block_string(self):
        block_data = "060750615003005"
        identifier_input = self.client.block.get_identifier_input(block_data)
        self.assertEqual([{"block_id": "060750615003005"}], identifier_input)

    def test_get_block_input_with_list_of_block_strings(self):
        block_data = ["060750615003005", "012345678901234"]
        identifier_input = self.client.block.get_identifier_input(block_data)
        self.assertEqual([{"block_id": "060750615003005"}, {"block_id": "012345678901234"}],
                         identifier_input)

    def test_get_block_input_with_dict(self):
        block_data = {"block_id": "060750615003005", "meta": "someId"}
        identifier_input = self.client.block.get_identifier_input(block_data)
        self.assertEqual([block_data], identifier_input)

    def test_get_block_input_with_dict_num_bins(self):
        block_data = {"block_id": "060750615003005", "num_bins": 5}
        identifier_input = self.client.block.get_identifier_input(block_data)
        self.assertEqual([block_data], identifier_input)

    def test_get_block_input_with_dict_property_type(self):
        block_data = {"block_id": "060750615003005", "property_type": "SFD"}
        identifier_input = self.client.block.get_identifier_input(block_data)
        self.assertEqual([block_data],
                         identifier_input)

    def test_get_block_input_with_list_of_dicts(self):
        block_data = [{"block_id": "060750615003005", "meta": "someId"},
                      {"block_id": "012345678901234", "meta": "someId2"}]
        identifier_input = self.client.block.get_identifier_input(block_data)
        self.assertEqual(block_data, identifier_input)

    def test_get_block_input_dict_with_invalid_key(self):
        block_data = {"block_id": "060750615003005", "color": "green"}
        with self.assertRaises(housecanary.exceptions.InvalidInputException):
            self.client.block.get_identifier_input(block_data)

    def test_get_block_input_dict_missing_block_id(self):
        block_data = {"num_bins": 5}
        with self.assertRaises(housecanary.exceptions.InvalidInputException):
            self.client.block.get_identifier_input(block_data)

    def test_histogram_baths(self):
        response = self.client.block.histogram_baths(self.test_data_num_bins)
        self.assertTrue(isinstance(response, BlockResponse))
        self.assertIsNotNone(response.json()[0]["block/histogram_baths"])

    def test_histogram_beds(self):
        response = self.client.block.histogram_beds(self.test_data_num_bins)
        self.assertTrue(isinstance(response, BlockResponse))
        self.assertIsNotNone(response.json()[0]["block/histogram_beds"])

    def test_histogram_building_area(self):
        response = self.client.block.histogram_building_area(self.test_data_num_bins)
        self.assertTrue(isinstance(response, BlockResponse))
        self.assertIsNotNone(response.json()[0]["block/histogram_building_area"])

    def test_histogram_value(self):
        response = self.client.block.histogram_value(self.test_data_num_bins)
        self.assertTrue(isinstance(response, BlockResponse))
        self.assertIsNotNone(response.json()[0]["block/histogram_value"])

    def test_histogram_value_sqft(self):
        response = self.client.block.histogram_value_sqft(self.test_data_num_bins)
        self.assertTrue(isinstance(response, BlockResponse))
        self.assertIsNotNone(response.json()[0]["block/histogram_value_sqft"])

    def test_rental_value_distribution(self):
        response = self.client.block.rental_value_distribution(self.test_data_prop_type)
        self.assertTrue(isinstance(response, BlockResponse))
        self.assertIsNotNone(response.json()[0]["block/rental_value_distribution"])

    def test_value_distribution(self):
        response = self.client.block.value_distribution(self.test_data_prop_type)
        self.assertTrue(isinstance(response, BlockResponse))
        self.assertIsNotNone(response.json()[0]["block/value_distribution"])

    def test_value_ts(self):
        response = self.client.block.value_ts(self.test_data_prop_type)
        self.assertTrue(isinstance(response, BlockResponse))
        self.assertIsNotNone(response.json()[0]["block/value_ts"])

    def test_value_ts_forecast(self):
        response = self.client.block.value_ts_forecast(self.test_data_prop_type)
        self.assertTrue(isinstance(response, BlockResponse))
        self.assertIsNotNone(response.json()[0]["block/value_ts_forecast"])

    def test_value_ts_historical(self):
        response = self.client.block.value_ts_historical(self.test_data_prop_type)
        self.assertTrue(isinstance(response, BlockResponse))
        self.assertIsNotNone(response.json()[0]["block/value_ts_historical"])

    def test_component_mget(self):
        components = ["block/value_ts", "block/value_distribution"]
        response = self.client.block.component_mget(self.test_data_prop_type, components)
        self.assertTrue(isinstance(response, BlockResponse))
        self.assertIsNotNone(response.json()[0]["block/value_ts"])
        self.assertIsNotNone(response.json()[0]["block/value_distribution"])


class ZipComponentWrapperTestCase(unittest.TestCase):
    """Tests for the ZipComponentWrapper class."""

    def setUp(self):
        self.client = ApiClient()
        self.test_data = [{"zipcode": "90274", "meta": "block1"}]

    def test_get_zip_input_with_single_zipcode_string(self):
        zip_data = "01960"
        identifier_input = self.client.zip.get_identifier_input(zip_data)
        self.assertEqual([{"zipcode": "01960"}], identifier_input)

    def test_get_zip_input_with_list_of_zipcode_strings(self):
        zip_data = ["01960", "01960"]
        identifier_input = self.client.zip.get_identifier_input(zip_data)
        self.assertEqual([{"zipcode": "01960"}, {"zipcode": "01960"}],
                         identifier_input)

    def test_get_zip_input_with_dict(self):
        zip_data = {"zipcode": "01960", "meta": "someId"}
        identifier_input = self.client.zip.get_identifier_input(zip_data)
        self.assertEqual([zip_data], identifier_input)

    def test_get_zip_input_with_list_of_dicts(self):
        zip_data = [{"zipcode": "01960", "meta": "someId"},
                    {"zipcode": "01960", "meta": "someId2"}]
        identifier_input = self.client.zip.get_identifier_input(zip_data)
        self.assertEqual(zip_data, identifier_input)

    def test_get_zip_input_dict_with_invalid_key(self):
        zip_data = {"zipcode": "01960", "color": "green"}
        with self.assertRaises(housecanary.exceptions.InvalidInputException):
            self.client.zip.get_identifier_input(zip_data)

    def test_get_zip_input_dict_missing_zipcode(self):
        zip_data = {"meta": "test"}
        with self.assertRaises(housecanary.exceptions.InvalidInputException):
            self.client.zip.get_identifier_input(zip_data)

    def test_hpi_forecast(self):
        response = self.client.zip.hpi_forecast(self.test_data)
        self.assertTrue(isinstance(response, ZipCodeResponse))
        self.assertIsNotNone(response.json()[0]["zip/hpi_forecast"])

    def test_hpi_historical(self):
        response = self.client.zip.hpi_historical(self.test_data)
        self.assertTrue(isinstance(response, ZipCodeResponse))
        self.assertIsNotNone(response.json()[0]["zip/hpi_historical"])

    def test_volatility(self):
        response = self.client.zip.volatility(self.test_data)
        self.assertTrue(isinstance(response, ZipCodeResponse))
        self.assertIsNotNone(response.json()[0]["zip/volatility"])

    def test_details(self):
        response = self.client.zip.details(self.test_data)
        self.assertTrue(isinstance(response, ZipCodeResponse))
        self.assertIsNotNone(response.json()[0]["zip/details"])

    def test_hpi_ts(self):
        response = self.client.zip.hpi_ts(self.test_data)
        self.assertTrue(isinstance(response, ZipCodeResponse))
        self.assertIsNotNone(response.json()[0]["zip/hpi_ts"])

    def test_hpi_ts_forecast(self):
        response = self.client.zip.hpi_ts_forecast(self.test_data)
        self.assertTrue(isinstance(response, ZipCodeResponse))
        self.assertIsNotNone(response.json()[0]["zip/hpi_ts_forecast"])

    def test_hpi_ts_historical(self):
        response = self.client.zip.hpi_ts_historical(self.test_data)
        self.assertTrue(isinstance(response, ZipCodeResponse))
        self.assertIsNotNone(response.json()[0]["zip/hpi_ts_historical"])

    def test_component_mget(self):
        components = ["zip/details", "zip/volatility"]
        response = self.client.zip.component_mget(self.test_data, components)
        self.assertTrue(isinstance(response, ZipCodeResponse))
        self.assertIsNotNone(response.json()[0]["zip/details"])
        self.assertIsNotNone(response.json()[0]["zip/volatility"])


class MsaComponentWrapperTestCase(unittest.TestCase):
    """Tests for the MsaComponentWrapper class."""

    def setUp(self):
        self.client = ApiClient()
        self.test_data = [{"msa": "41860", "meta": "block1"}]

    def test_get_msa_input_with_single_msa_string(self):
        msa_data = "41860"
        identifier_input = self.client.msa.get_identifier_input(msa_data)
        self.assertEqual([{"msa": "41860"}], identifier_input)

    def test_get_msa_input_with_list_of_msa_strings(self):
        msa_data = ["41860", "40928"]
        identifier_input = self.client.msa.get_identifier_input(msa_data)
        self.assertEqual([{"msa": "41860"}, {"msa": "40928"}],
                         identifier_input)

    def test_get_msa_input_with_dict(self):
        msa_data = {"msa": "41860", "meta": "someId"}
        identifier_input = self.client.msa.get_identifier_input(msa_data)
        self.assertEqual([msa_data], identifier_input)

    def test_get_msa_input_with_list_of_dicts(self):
        msa_data = [{"msa": "41860", "meta": "someId"},
                    {"msa": "41860", "meta": "someId2"}]
        identifier_input = self.client.msa.get_identifier_input(msa_data)
        self.assertEqual(msa_data, identifier_input)

    def test_get_msa_input_dict_with_invalid_key(self):
        msa_data = {"msa": "41860", "color": "green"}
        with self.assertRaises(housecanary.exceptions.InvalidInputException):
            self.client.msa.get_identifier_input(msa_data)

    def test_get_msa_input_dict_missing_msa(self):
        msa_data = {"meta": "test"}
        with self.assertRaises(housecanary.exceptions.InvalidInputException):
            self.client.msa.get_identifier_input(msa_data)

    def test_details(self):
        response = self.client.msa.details(self.test_data)
        self.assertTrue(isinstance(response, MsaResponse))
        self.assertIsNotNone(response.json()[0]["msa/details"])

    def test_hpi_ts(self):
        response = self.client.msa.hpi_ts(self.test_data)
        self.assertTrue(isinstance(response, MsaResponse))
        self.assertIsNotNone(response.json()[0]["msa/hpi_ts"])

    def test_hpi_ts_forecast(self):
        response = self.client.msa.hpi_ts_forecast(self.test_data)
        self.assertTrue(isinstance(response, MsaResponse))
        self.assertIsNotNone(response.json()[0]["msa/hpi_ts_forecast"])

    def test_hpi_ts_historical(self):
        response = self.client.msa.hpi_ts_historical(self.test_data)
        self.assertTrue(isinstance(response, MsaResponse))
        self.assertIsNotNone(response.json()[0]["msa/hpi_ts_historical"])

    def test_component_mget(self):
        components = ["msa/details", "msa/hpi_ts"]
        response = self.client.msa.component_mget(self.test_data, components)
        self.assertTrue(isinstance(response, MsaResponse))
        self.assertIsNotNone(response.json()[0]["msa/details"])
        self.assertIsNotNone(response.json()[0]["msa/hpi_ts"])


if __name__ == "__main__":
    unittest.main()
