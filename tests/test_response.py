# pylint: disable=missing-docstring

import unittest
import requests_mock
from housecanary.apiclient import ApiClient
from housecanary.object import Property
from housecanary.object import Block
from housecanary.object import ZipCode
from housecanary.object import Msa


@requests_mock.Mocker()
class PropertyResponseTestCase(unittest.TestCase):
    def setUp(self):
        self.client = ApiClient()
        self.test_data = [{"address": "43 Valmonte Plaza", "zipcode": "90274"}]
        self.headers = {'content-type': 'application/json', 'X-RateLimit-Limit': '5000', 'X-RateLimit-Reset': '1491920221', 'X-RateLimit-Period': '60', 'X-RateLimit-Remaining': '4999'}
        self.response = [{'property/value': {'api_code_description': 'ok', 'result': {'value': {'price_upr': 1780318, 'fsd': 0.0836871, 'price_mean': 1642834, 'price_lwr': 1505350}}, 'api_code': 0}, 'address_info': {'state': 'CA', 'address_full': '43 Valmonte Plz Palos Verdes Estates CA 90274', 'block_id': '060376703241005', 'slug': '43-Valmonte-Plz-Palos-Verdes-Estates-CA-90274', 'msa': '31080', 'zipcode': '90274', 'county_fips': '06037', 'city': 'Palos Verdes Estates', 'geo_precision': 'rooftop', 'unit': None, 'address': '43 Valmonte Plz', 'lat': 33.79814, 'zipcode_plus4': '1444', 'metrodiv': '31084', 'lng': -118.36455}}]
        self.multi_property_response = [{'property/value': {'api_code_description': 'ok', 'result': {'value': {'price_upr': 1780318, 'fsd': 0.0836871, 'price_mean': 1642834, 'price_lwr': 1505350}}, 'api_code': 0}, 'address_info': {'state': 'CA', 'address_full': '43 Valmonte Plz Palos Verdes Estates CA 90274', 'block_id': '060376703241005', 'slug': '43-Valmonte-Plz-Palos-Verdes-Estates-CA-90274', 'msa': '31080', 'zipcode': '90274', 'county_fips': '06037', 'city': 'Palos Verdes Estates', 'geo_precision': 'rooftop', 'unit': None, 'address': '43 Valmonte Plz', 'lat': 33.79814, 'zipcode_plus4': '1444', 'metrodiv': '31084', 'lng': -118.36455}}, {'property/value': {'api_code_description': 'no content', 'result': None, 'api_code': 204}, 'address_info': {'state': None, 'address_full': None, 'block_id': None, 'slug': None, 'msa': None, 'zipcode': None, 'county_fips': None, 'city': None, 'geo_precision': 'unknown', 'unit': None, 'address': None, 'lat': None, 'zipcode_plus4': None, 'metrodiv': None, 'lng': None}}]
        self.error_response = [{'property/value': {'api_code_description': 'no content', 'result': None, 'api_code': 204}, 'address_info': {'state': None, 'address_full': None, 'block_id': None, 'slug': None, 'msa': None, 'zipcode': None, 'county_fips': None, 'city': None, 'geo_precision': 'unknown', 'unit': None, 'address': None, 'lat': None, 'zipcode_plus4': None, 'metrodiv': None, 'lng': None}}]

    def test_endpoint_name(self, mock):
        mock.get("/v2/property/value", headers=self.headers, json=self.response)
        response = self.client.fetch("property/value", self.test_data)
        self.assertEqual(response.endpoint_name, "property/value")

    def test_json(self, mock):
        mock.get("/v2/property/value", headers=self.headers, json=self.response)
        response = self.client.fetch("property/value", self.test_data)
        self.assertTrue(isinstance(response.json(), list))

    def test_response(self, mock):
        mock.get("/v2/property/value", headers=self.headers, json=self.response)
        response = self.client.fetch("property/value", self.test_data)
        self.assertIsNotNone(response.response)

    def test_get_object_errors(self, mock):
        mock.get("/v2/property/value", headers=self.headers, json=self.response)
        response = self.client.fetch("property/value", self.test_data)
        self.assertEqual(response.get_object_errors(), [])

    def test_get_object_errors_with_error(self, mock):
        mock.get("/v2/property/value", headers=self.headers, json=self.error_response)
        self.test_data[0]["zipcode"] = "00000"
        response = self.client.fetch("property/value", self.test_data)
        self.assertEqual(len(response.get_object_errors()), 1)

    def test_has_object_error(self, mock):
        mock.get("/v2/property/value", headers=self.headers, json=self.response)
        response = self.client.fetch("property/value", self.test_data)
        self.assertFalse(response.has_object_error())

    def test_has_object_error_with_error(self, mock):
        mock.get("/v2/property/value", headers=self.headers, json=self.error_response)
        self.test_data[0]["zipcode"] = "00000"
        response = self.client.fetch("property/value", self.test_data)
        self.assertTrue(response.has_object_error())

    def test_properties(self, mock):
        mock.get("/v2/property/value", headers=self.headers, json=self.response)
        response = self.client.fetch("property/value", self.test_data)
        self.assertTrue(len(response.properties()), 1)
        self.assertTrue(isinstance(response.properties()[0], Property))

    def test_properties_with_multiple(self, mock):
        mock.post("/v2/property/value", headers=self.headers, json=self.multi_property_response)
        self.test_data.append({"address": "85 Clay St", "zipcode": "02140"})
        response = self.client.fetch("property/value", self.test_data)
        self.assertTrue(len(response.properties()), 2)
        self.assertTrue(isinstance(response.properties()[0], Property))
        self.assertTrue(isinstance(response.properties()[1], Property))

    def test_response_rate_limits(self, mock):
        mock.get("/v2/property/value", headers=self.headers, json=self.response)
        response = self.client.fetch("property/value", self.test_data)
        self.assertTrue(isinstance(response.rate_limits, list))
        self.assertTrue(isinstance(response.rate_limits[0]['period'], str))


@requests_mock.Mocker()
class BlockResponseTestCase(unittest.TestCase):
    def setUp(self):
        self.client = ApiClient()
        self.test_data = [{"block_id": "060376703241005"}]
        self.headers = {'content-type': 'application/json', 'X-RateLimit-Limit': '5000', 'X-RateLimit-Reset': '1491920221', 'X-RateLimit-Period': '60', 'X-RateLimit-Remaining': '4999'}
        self.response = [{'block_info': {'block_id': '060376703241005'}, 'block/value_ts': {'api_code_description': 'ok', 'result': {'time_series': [{'value_sqft_median': 296.89, 'month': '1994-02-01', 'value_median': 513529}], 'property_type': 'SFD'}, 'api_code': 0}}]
        self.response_multi = [{'block_info': {'block_id': '060376703241005'}, 'block/value_ts': {'api_code_description': 'ok', 'result': {'time_series': [{'value_sqft_median': 296.89, 'month': '1994-02-01', 'value_median': 513529}], 'property_type': 'SFD'}, 'api_code': 0}}, {'block_info': {'block_id': '160376703241005'}, 'block/value_ts': {'api_code_description': 'ok', 'result': {'time_series': [{'value_sqft_median': 296.89, 'month': '1994-02-01', 'value_median': 513529}], 'property_type': 'SFD'}, 'api_code': 0}}]

    def test_blocks(self, mock):
        mock.get("/v2/block/value_ts", headers=self.headers, json=self.response)
        response = self.client.fetch("block/value_ts", self.test_data)
        self.assertTrue(len(response.blocks()), 1)
        self.assertTrue(isinstance(response.blocks()[0], Block))

    def test_blocks_with_multiple(self, mock):
        mock.post("/v2/block/value_ts", headers=self.headers, json=self.response_multi)
        self.test_data.append({"block_id": "160376703241005"})
        response = self.client.fetch("block/value_ts", self.test_data)
        self.assertTrue(len(response.blocks()), 2)
        self.assertTrue(isinstance(response.blocks()[0], Block))
        self.assertTrue(isinstance(response.blocks()[1], Block))


@requests_mock.Mocker()
class ZipCodeResponseTestCase(unittest.TestCase):
    def setUp(self):
        self.client = ApiClient()
        self.test_data = [{"zipcode": "90274"}]
        self.headers = {'content-type': 'application/json', 'X-RateLimit-Limit': '5000', 'X-RateLimit-Reset': '1491920221', 'X-RateLimit-Period': '60', 'X-RateLimit-Remaining': '4999'}
        self.response = [{'zip/details': {'api_code_description': 'ok', 'result': {'single_family': {'inventory_total': 78.538, 'price_median': 2748899.085, 'estimated_sales_total': None, 'days_on_market_median': 116.132, 'months_of_inventory_median': None, 'market_action_median': 62.34}, 'multi_family': {'inventory_total': None, 'price_median': None, 'estimated_sales_total': None, 'days_on_market_median': None, 'months_of_inventory_median': None, 'market_action_median': None}}, 'api_code': 0}, 'zipcode_info': {'zipcode': '90274'}}]
        self.response_multi = [{'zip/details': {'api_code_description': 'ok', 'result': {'single_family': {'inventory_total': 78.538, 'price_median': 2748899.085, 'estimated_sales_total': None, 'days_on_market_median': 116.132, 'months_of_inventory_median': None, 'market_action_median': 62.34}, 'multi_family': {'inventory_total': None, 'price_median': None, 'estimated_sales_total': None, 'days_on_market_median': None, 'months_of_inventory_median': None, 'market_action_median': None}}, 'api_code': 0}, 'zipcode_info': {'zipcode': '90274'}}, {'zip/details': {'api_code_description': 'ok', 'result': {'single_family': {'inventory_total': 28.462, 'price_median': 453311.462, 'estimated_sales_total': 24.908, 'days_on_market_median': 46.308, 'months_of_inventory_median': 1.143, 'market_action_median': 79.47}, 'multi_family': {'inventory_total': 8.923, 'price_median': 236076.923, 'estimated_sales_total': 6.73, 'days_on_market_median': 67.038, 'months_of_inventory_median': 1.326, 'market_action_median': 81.33}}, 'api_code': 0}, 'zipcode_info': {'zipcode': '01960'}}]

    def test_zipcodes(self, mock):
        mock.get("/v2/zip/details", headers=self.headers, json=self.response)
        response = self.client.fetch("zip/details", self.test_data)
        self.assertTrue(len(response.zipcodes()), 1)
        self.assertTrue(isinstance(response.zipcodes()[0], ZipCode))

    def test_zipcodes_with_multiple(self, mock):
        mock.post("/v2/zip/details", headers=self.headers, json=self.response_multi)
        self.test_data.append({"zipcode": "01960"})
        response = self.client.fetch("zip/details", self.test_data)
        self.assertTrue(len(response.zipcodes()), 2)
        self.assertTrue(isinstance(response.zipcodes()[0], ZipCode))
        self.assertTrue(isinstance(response.zipcodes()[1], ZipCode))


@requests_mock.Mocker()
class MsaResponseTestCase(unittest.TestCase):
    def setUp(self):
        self.client = ApiClient()
        self.test_data = [{"msa": "41860"}]
        self.headers = {'content-type': 'application/json', 'X-RateLimit-Limit': '5000', 'X-RateLimit-Reset': '1491920221', 'X-RateLimit-Period': '60', 'X-RateLimit-Remaining': '4999'}
        self.response = [{'msa_info': {'msa': '41860', 'msa_name': 'San Francisco-Oakland-Hayward, CA'}, 'msa/details': {'api_code_description': 'ok', 'result': {'returns_5': 0.8724, 'cagr_1': 0.0673, 'cagr_5': 0.1336, 'max_12mo_loss': -0.210943, 'cagr_10': 0.0183, 'returns_1': 0.0673, 'risk_12mo_loss': 0.080268, 'cagr_20': 0.0658, 'returns_10': 0.1985}, 'api_code': 0}}]
        self.response_multi = [{'msa_info': {'msa': '41860', 'msa_name': 'San Francisco-Oakland-Hayward, CA'}, 'msa/details': {'api_code_description': 'ok', 'result': {'returns_5': 0.8724, 'cagr_1': 0.0673, 'cagr_5': 0.1336, 'max_12mo_loss': -0.210943, 'cagr_10': 0.0183, 'returns_1': 0.0673, 'risk_12mo_loss': 0.080268, 'cagr_20': 0.0658, 'returns_10': 0.1985}, 'api_code': 0}}, {'msa_info': {'msa': '41861', 'msa_name': 'San Francisco-Oakland-Hayward, CA'}, 'msa/details': {'api_code_description': 'ok', 'result': {'returns_5': 0.8724, 'cagr_1': 0.0673, 'cagr_5': 0.1336, 'max_12mo_loss': -0.210943, 'cagr_10': 0.0183, 'returns_1': 0.0673, 'risk_12mo_loss': 0.080268, 'cagr_20': 0.0658, 'returns_10': 0.1985}, 'api_code': 0}}]

    def test_msas(self, mock):
        mock.get("/v2/msa/details", headers=self.headers, json=self.response)
        response = self.client.fetch("msa/details", self.test_data)
        self.assertTrue(len(response.msas()), 1)
        self.assertTrue(isinstance(response.msas()[0], Msa))

    def test_msas_with_multiple(self, mock):
        mock.post("/v2/msa/details", headers=self.headers, json=self.response_multi)
        self.test_data.append({"msa": "41861"})
        response = self.client.fetch("msa/details", self.test_data)
        self.assertTrue(len(response.msas()), 2)
        self.assertTrue(isinstance(response.msas()[0], Msa))
        self.assertTrue(isinstance(response.msas()[1], Msa))


if __name__ == "__main__":
    unittest.main()
