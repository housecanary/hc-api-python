import unittest
import requests_mock
import os
import shutil
from housecanary.hc_api_export import hc_api_export


@requests_mock.Mocker()
class HcApiExportTestCase(unittest.TestCase):
    """Tests for the hc_api_export tool"""

    def setUp(self):
        self.output_excel_file = 'unittest_hc_api_export.xlsx'
        self.output_csv_path = 'unittest_housecanary_csv'
        self._remove_test_output()
        self.headers = {"content-type": "application/json"}
        # self.response = [{'property/value': {'api_code_description': 'ok', 'result': {'value': 'test'}}, 'address_info': 'test'}]

    def tearDown(self):
        self._remove_test_output()

    def _remove_test_output(self):
        if os.path.exists(self.output_excel_file):
            os.remove(self.output_excel_file)
        if os.path.exists(self.output_csv_path):
            shutil.rmtree(self.output_csv_path)

    def get_docopt_args(self, output_type, endpoints, input_file):
        return {
            '--help': False,
            '--key': 'test_key',
            '--output': self.output_excel_file,
            '--path': self.output_csv_path,
            '--retry': False,
            '--secret': 'test_secret',
            '--type': output_type,
            '-h': False,
            '<endpoints>': endpoints,
            '<input>': input_file
        }

    def _test_excel_output(self, docopt_args):
        self.assertFalse(os.path.exists(self.output_excel_file))
        hc_api_export.hc_api_export(docopt_args)
        self.assertTrue(os.path.exists(self.output_excel_file))

    def _test_csv_output(self, docopt_args):
        self.assertFalse(os.path.exists(self.output_csv_path))
        hc_api_export.hc_api_export(docopt_args)
        self.assertTrue(os.path.exists(self.output_csv_path))

    def test_hc_api_export_property_excel(self, mock):
        response = [{'address_info': {'city': 'Palos Verdes Estates', 'county_fips': '06037', 'geo_precision': 'rooftop', 'block_id': '060376703241005', 'zipcode': '90274', 'address_full': '43 Valmonte Plz Palos Verdes Estates CA 90274', 'zipcode_plus4': '1444', 'state': 'CA', 'metrodiv': '31084', 'unit': None, 'address': '43 Valmonte Plz', 'lat': 33.79814, 'lng': -118.36455, 'slug': '43-Valmonte-Plz-Palos-Verdes-Estates-CA-90274', 'msa': '31080'}, 'property/value': {'api_code_description': 'ok', 'api_code': 0, 'result': {'value': {'price_upr': 1780318, 'price_lwr': 1505350, 'price_mean': 1642834, 'fsd': 0.0836871}}}}, {'address_info': {'city': 'Pasadena', 'county_fips': '06037', 'geo_precision': 'rooftop', 'block_id': '060374632002006', 'zipcode': '91107', 'address_full': '244 S Altadena Dr Pasadena CA 91107', 'zipcode_plus4': '4820', 'state': 'CA', 'metrodiv': '31084', 'unit': None, 'address': '244 S Altadena Dr', 'lat': 34.14182, 'lng': -118.09833, 'slug': '244-S-Altadena-Dr-Pasadena-CA-91107', 'msa': '31080'}, 'property/value': {'api_code_description': 'ok', 'api_code': 0, 'result': {'value': {'price_upr': 672556, 'price_lwr': 615548, 'price_mean': 644052, 'fsd': 0.0442573}}}}]
        mock.post("/v2/property/component_mget", headers=self.headers, json=response)
        self._test_excel_output(self.get_docopt_args(
            'excel', 'property/*', './tests/test_files/test_input.csv'
        ))

    def test_hc_api_export_property_csv(self, mock):
        response = [{'address_info': {'city': 'Palos Verdes Estates', 'county_fips': '06037', 'geo_precision': 'rooftop', 'block_id': '060376703241005', 'zipcode': '90274', 'address_full': '43 Valmonte Plz Palos Verdes Estates CA 90274', 'zipcode_plus4': '1444', 'state': 'CA', 'metrodiv': '31084', 'unit': None, 'address': '43 Valmonte Plz', 'lat': 33.79814, 'lng': -118.36455, 'slug': '43-Valmonte-Plz-Palos-Verdes-Estates-CA-90274', 'msa': '31080'}, 'property/value': {'api_code_description': 'ok', 'api_code': 0, 'result': {'value': {'price_upr': 1780318, 'price_lwr': 1505350, 'price_mean': 1642834, 'fsd': 0.0836871}}}}, {'address_info': {'city': 'Pasadena', 'county_fips': '06037', 'geo_precision': 'rooftop', 'block_id': '060374632002006', 'zipcode': '91107', 'address_full': '244 S Altadena Dr Pasadena CA 91107', 'zipcode_plus4': '4820', 'state': 'CA', 'metrodiv': '31084', 'unit': None, 'address': '244 S Altadena Dr', 'lat': 34.14182, 'lng': -118.09833, 'slug': '244-S-Altadena-Dr-Pasadena-CA-91107', 'msa': '31080'}, 'property/value': {'api_code_description': 'ok', 'api_code': 0, 'result': {'value': {'price_upr': 672556, 'price_lwr': 615548, 'price_mean': 644052, 'fsd': 0.0442573}}}}]
        mock.post("/v2/property/component_mget", headers=self.headers, json=response)
        self._test_csv_output(self.get_docopt_args(
            'csv', 'property/*', './tests/test_files/test_input.csv'
        ))

    def test_hc_api_export_excel_property_city_state(self, mock):
        response = [{'address_info': {'city': 'Palos Verdes Estates', 'county_fips': '06037', 'geo_precision': 'rooftop', 'block_id': '060376703241005', 'zipcode': '90274', 'address_full': '43 Valmonte Plz Palos Verdes Estates CA 90274', 'zipcode_plus4': '1444', 'state': 'CA', 'metrodiv': '31084', 'unit': None, 'address': '43 Valmonte Plz', 'lat': 33.79814, 'lng': -118.36455, 'slug': '43-Valmonte-Plz-Palos-Verdes-Estates-CA-90274', 'msa': '31080'}, 'property/value': {'api_code_description': 'ok', 'api_code': 0, 'result': {'value': {'price_upr': 1780318, 'price_lwr': 1505350, 'price_mean': 1642834, 'fsd': 0.0836871}}}}, {'address_info': {'city': 'Pasadena', 'county_fips': '06037', 'geo_precision': 'rooftop', 'block_id': '060374632002006', 'zipcode': '91107', 'address_full': '244 S Altadena Dr Pasadena CA 91107', 'zipcode_plus4': '4820', 'state': 'CA', 'metrodiv': '31084', 'unit': None, 'address': '244 S Altadena Dr', 'lat': 34.14182, 'lng': -118.09833, 'slug': '244-S-Altadena-Dr-Pasadena-CA-91107', 'msa': '31080'}, 'property/value': {'api_code_description': 'ok', 'api_code': 0, 'result': {'value': {'price_upr': 672556, 'price_lwr': 615548, 'price_mean': 644052, 'fsd': 0.0442573}}}}]
        mock.post("/v2/property/component_mget", headers=self.headers, json=response)
        self._test_excel_output(self.get_docopt_args(
            'excel', 'property/*', './sample_input/sample-input-city-state.csv'
        ))

    def test_hc_api_export_csv_property_city_state(self, mock):
        response = [{'address_info': {'city': 'Palos Verdes Estates', 'county_fips': '06037', 'geo_precision': 'rooftop', 'block_id': '060376703241005', 'zipcode': '90274', 'address_full': '43 Valmonte Plz Palos Verdes Estates CA 90274', 'zipcode_plus4': '1444', 'state': 'CA', 'metrodiv': '31084', 'unit': None, 'address': '43 Valmonte Plz', 'lat': 33.79814, 'lng': -118.36455, 'slug': '43-Valmonte-Plz-Palos-Verdes-Estates-CA-90274', 'msa': '31080'}, 'property/value': {'api_code_description': 'ok', 'api_code': 0, 'result': {'value': {'price_upr': 1780318, 'price_lwr': 1505350, 'price_mean': 1642834, 'fsd': 0.0836871}}}}, {'address_info': {'city': 'Pasadena', 'county_fips': '06037', 'geo_precision': 'rooftop', 'block_id': '060374632002006', 'zipcode': '91107', 'address_full': '244 S Altadena Dr Pasadena CA 91107', 'zipcode_plus4': '4820', 'state': 'CA', 'metrodiv': '31084', 'unit': None, 'address': '244 S Altadena Dr', 'lat': 34.14182, 'lng': -118.09833, 'slug': '244-S-Altadena-Dr-Pasadena-CA-91107', 'msa': '31080'}, 'property/value': {'api_code_description': 'ok', 'api_code': 0, 'result': {'value': {'price_upr': 672556, 'price_lwr': 615548, 'price_mean': 644052, 'fsd': 0.0442573}}}}]
        mock.post("/v2/property/component_mget", headers=self.headers, json=response)
        self._test_csv_output(self.get_docopt_args(
            'csv', 'property/*', './sample_input/sample-input-city-state.csv'
        ))

    def test_hc_api_export_excel_property_slug(self, mock):
        response = [{'address_info': {'city': 'Palos Verdes Estates', 'county_fips': '06037', 'geo_precision': 'rooftop', 'block_id': '060376703241005', 'zipcode': '90274', 'address_full': '43 Valmonte Plz Palos Verdes Estates CA 90274', 'zipcode_plus4': '1444', 'state': 'CA', 'metrodiv': '31084', 'unit': None, 'address': '43 Valmonte Plz', 'lat': 33.79814, 'lng': -118.36455, 'slug': '43-Valmonte-Plz-Palos-Verdes-Estates-CA-90274', 'msa': '31080'}, 'property/value': {'api_code_description': 'ok', 'api_code': 0, 'result': {'value': {'price_upr': 1780318, 'price_lwr': 1505350, 'price_mean': 1642834, 'fsd': 0.0836871}}}}, {'address_info': {'city': 'Pasadena', 'county_fips': '06037', 'geo_precision': 'rooftop', 'block_id': '060374632002006', 'zipcode': '91107', 'address_full': '244 S Altadena Dr Pasadena CA 91107', 'zipcode_plus4': '4820', 'state': 'CA', 'metrodiv': '31084', 'unit': None, 'address': '244 S Altadena Dr', 'lat': 34.14182, 'lng': -118.09833, 'slug': '244-S-Altadena-Dr-Pasadena-CA-91107', 'msa': '31080'}, 'property/value': {'api_code_description': 'ok', 'api_code': 0, 'result': {'value': {'price_upr': 672556, 'price_lwr': 615548, 'price_mean': 644052, 'fsd': 0.0442573}}}}]
        mock.post("/v2/property/component_mget", headers=self.headers, json=response)
        self._test_excel_output(self.get_docopt_args(
            'excel', 'property/*', './sample_input/sample-input-slugs.csv'
        ))

    def test_hc_api_export_csv_property_slug(self, mock):
        response = [{'address_info': {'city': 'Palos Verdes Estates', 'county_fips': '06037', 'geo_precision': 'rooftop', 'block_id': '060376703241005', 'zipcode': '90274', 'address_full': '43 Valmonte Plz Palos Verdes Estates CA 90274', 'zipcode_plus4': '1444', 'state': 'CA', 'metrodiv': '31084', 'unit': None, 'address': '43 Valmonte Plz', 'lat': 33.79814, 'lng': -118.36455, 'slug': '43-Valmonte-Plz-Palos-Verdes-Estates-CA-90274', 'msa': '31080'}, 'property/value': {'api_code_description': 'ok', 'api_code': 0, 'result': {'value': {'price_upr': 1780318, 'price_lwr': 1505350, 'price_mean': 1642834, 'fsd': 0.0836871}}}}, {'address_info': {'city': 'Pasadena', 'county_fips': '06037', 'geo_precision': 'rooftop', 'block_id': '060374632002006', 'zipcode': '91107', 'address_full': '244 S Altadena Dr Pasadena CA 91107', 'zipcode_plus4': '4820', 'state': 'CA', 'metrodiv': '31084', 'unit': None, 'address': '244 S Altadena Dr', 'lat': 34.14182, 'lng': -118.09833, 'slug': '244-S-Altadena-Dr-Pasadena-CA-91107', 'msa': '31080'}, 'property/value': {'api_code_description': 'ok', 'api_code': 0, 'result': {'value': {'price_upr': 672556, 'price_lwr': 615548, 'price_mean': 644052, 'fsd': 0.0442573}}}}]
        mock.post("/v2/property/component_mget", headers=self.headers, json=response)
        self._test_csv_output(self.get_docopt_args(
            'csv', 'property/*', './sample_input/sample-input-slugs.csv'
        ))

    def test_hc_api_export_zip_excel(self, mock):
        response = [{'zip/details': {'api_code_description': 'ok', 'api_code': 0, 'result': {'multi_family': {'inventory_total': None, 'price_median': None, 'estimated_sales_total': None, 'market_action_median': None, 'months_of_inventory_median': None, 'days_on_market_median': None}, 'single_family': {'inventory_total': 78.538, 'price_median': 2748899.085, 'estimated_sales_total': None, 'market_action_median': 62.34, 'months_of_inventory_median': None, 'days_on_market_median': 116.132}}}, 'meta': 'Area 1', 'zipcode_info': {'zipcode': '90274'}}, {'zip/details': {'api_code_description': 'ok', 'api_code': 0, 'result': {'multi_family': {'inventory_total': 11.385, 'price_median': 581361.538, 'estimated_sales_total': 8.46, 'market_action_median': 69.34, 'months_of_inventory_median': 1.346, 'days_on_market_median': 29.615}, 'single_family': {'inventory_total': 54.385, 'price_median': 1148846.077, 'estimated_sales_total': 22.229, 'market_action_median': 57.87, 'months_of_inventory_median': 2.447, 'days_on_market_median': 74.846}}}, 'meta': 'Area 2', 'zipcode_info': {'zipcode': '91107'}}]
        mock.post("/v2/zip/component_mget", headers=self.headers, json=response)
        self._test_excel_output(self.get_docopt_args(
            'excel', 'zip/*', './sample_input/sample-input-zipcodes.csv'
        ))

    def test_hc_api_export_zip_csv(self, mock):
        response = [{'zip/details': {'api_code_description': 'ok', 'api_code': 0, 'result': {'multi_family': {'inventory_total': None, 'price_median': None, 'estimated_sales_total': None, 'market_action_median': None, 'months_of_inventory_median': None, 'days_on_market_median': None}, 'single_family': {'inventory_total': 78.538, 'price_median': 2748899.085, 'estimated_sales_total': None, 'market_action_median': 62.34, 'months_of_inventory_median': None, 'days_on_market_median': 116.132}}}, 'meta': 'Area 1', 'zipcode_info': {'zipcode': '90274'}}, {'zip/details': {'api_code_description': 'ok', 'api_code': 0, 'result': {'multi_family': {'inventory_total': 11.385, 'price_median': 581361.538, 'estimated_sales_total': 8.46, 'market_action_median': 69.34, 'months_of_inventory_median': 1.346, 'days_on_market_median': 29.615}, 'single_family': {'inventory_total': 54.385, 'price_median': 1148846.077, 'estimated_sales_total': 22.229, 'market_action_median': 57.87, 'months_of_inventory_median': 2.447, 'days_on_market_median': 74.846}}}, 'meta': 'Area 2', 'zipcode_info': {'zipcode': '91107'}}]
        mock.post("/v2/zip/component_mget", headers=self.headers, json=response)
        self._test_csv_output(self.get_docopt_args(
            'csv', 'zip/*', './sample_input/sample-input-zipcodes.csv'
        ))

    def test_hc_api_export_block_excel(self, mock):
        response = [{'block/value_distribution': {'api_code_description': 'ok', 'api_code': 0, 'result': {'value_sqft_50': 814.2, 'value_min': 967440, 'value_25': 1141837, 'value_sqft_max': 900.7, 'value_sqft_mean': 812.4, 'value_sqft_count': 13, 'value_sqft_min': 709.2, 'value_max': 2141477, 'value_sqft_25': 798.0, 'value_sqft_95': 883.4, 'value_5': 1043104, 'value_95': 1883893, 'value_50': 1358392, 'value_count': 13, 'value_sd': 312382, 'value_sqft_5': 724.2, 'value_mean': 1382563, 'value_sqft_75': 842.4, 'property_type': 'SFD', 'value_75': 1445081, 'value_sqft_sd': 51.5}}, 'block_info': {'block_id': '060376703241005'}}, {'block/value_distribution': {'api_code_description': 'ok', 'api_code': 0, 'result': {'value_sqft_50': 562.0, 'value_min': 644052, 'value_25': 688884, 'value_sqft_max': 670.5, 'value_sqft_mean': 591.1, 'value_sqft_count': 6, 'value_sqft_min': 542.2, 'value_max': 1214631, 'value_sqft_25': 561.8, 'value_sqft_95': 664.9, 'value_5': 653522, 'value_95': 1102067, 'value_50': 713156, 'value_count': 6, 'value_sd': 212494, 'value_sqft_5': 547.1, 'value_mean': 788550, 'value_sqft_75': 626.5, 'property_type': 'SFD', 'value_75': 752425, 'value_sqft_sd': 53.8}}, 'block_info': {'block_id': '060374632002006'}}]
        mock.post("/v2/block/component_mget", headers=self.headers, json=response)
        self._test_excel_output(self.get_docopt_args(
            'excel', 'block/*', './sample_input/sample-input-blocks.csv'
        ))

    def test_hc_api_export_block_csv(self, mock):
        response = [{'block/value_distribution': {'api_code_description': 'ok', 'api_code': 0, 'result': {'value_sqft_50': 814.2, 'value_min': 967440, 'value_25': 1141837, 'value_sqft_max': 900.7, 'value_sqft_mean': 812.4, 'value_sqft_count': 13, 'value_sqft_min': 709.2, 'value_max': 2141477, 'value_sqft_25': 798.0, 'value_sqft_95': 883.4, 'value_5': 1043104, 'value_95': 1883893, 'value_50': 1358392, 'value_count': 13, 'value_sd': 312382, 'value_sqft_5': 724.2, 'value_mean': 1382563, 'value_sqft_75': 842.4, 'property_type': 'SFD', 'value_75': 1445081, 'value_sqft_sd': 51.5}}, 'block_info': {'block_id': '060376703241005'}}, {'block/value_distribution': {'api_code_description': 'ok', 'api_code': 0, 'result': {'value_sqft_50': 562.0, 'value_min': 644052, 'value_25': 688884, 'value_sqft_max': 670.5, 'value_sqft_mean': 591.1, 'value_sqft_count': 6, 'value_sqft_min': 542.2, 'value_max': 1214631, 'value_sqft_25': 561.8, 'value_sqft_95': 664.9, 'value_5': 653522, 'value_95': 1102067, 'value_50': 713156, 'value_count': 6, 'value_sd': 212494, 'value_sqft_5': 547.1, 'value_mean': 788550, 'value_sqft_75': 626.5, 'property_type': 'SFD', 'value_75': 752425, 'value_sqft_sd': 53.8}}, 'block_info': {'block_id': '060374632002006'}}]
        mock.post("/v2/block/component_mget", headers=self.headers, json=response)
        self._test_csv_output(self.get_docopt_args(
            'csv', 'block/*', './sample_input/sample-input-blocks.csv'
        ))

    def test_hc_api_export_msa_excel(self, mock):
        response = [{'msa/details': {'api_code_description': 'ok', 'api_code': 0, 'result': {'cagr_1': 0.0697, 'cagr_10': 0.0036, 'cagr_5': 0.0984, 'returns_10': 0.0363, 'max_12mo_loss': -0.217967, 'risk_12mo_loss': 0.088535, 'returns_1': 0.0697, 'cagr_20': 0.0648, 'returns_5': 0.5991}}, 'msa_info': {'msa_name': 'Los Angeles-Long Beach-Anaheim, CA', 'msa': '31080'}}, {'msa/details': {'api_code_description': 'ok', 'api_code': 0, 'result': {'cagr_1': 0.0738, 'cagr_10': -0.0299, 'cagr_5': 0.1406, 'returns_10': -0.2615, 'max_12mo_loss': -0.355033, 'risk_12mo_loss': 0.108988, 'returns_1': 0.0738, 'cagr_20': 0.0276, 'returns_5': 0.9303}}, 'msa_info': {'msa_name': 'Las Vegas-Henderson-Paradise, NV', 'msa': '29820'}}]
        mock.post("/v2/msa/component_mget", headers=self.headers, json=response)
        self._test_excel_output(self.get_docopt_args(
            'excel', 'msa/*', './sample_input/sample-input-msas.csv'
        ))

    def test_hc_api_export_msa_csv(self, mock):
        response = [{'msa/details': {'api_code_description': 'ok', 'api_code': 0, 'result': {'cagr_1': 0.0697, 'cagr_10': 0.0036, 'cagr_5': 0.0984, 'returns_10': 0.0363, 'max_12mo_loss': -0.217967, 'risk_12mo_loss': 0.088535, 'returns_1': 0.0697, 'cagr_20': 0.0648, 'returns_5': 0.5991}}, 'msa_info': {'msa_name': 'Los Angeles-Long Beach-Anaheim, CA', 'msa': '31080'}}, {'msa/details': {'api_code_description': 'ok', 'api_code': 0, 'result': {'cagr_1': 0.0738, 'cagr_10': -0.0299, 'cagr_5': 0.1406, 'returns_10': -0.2615, 'max_12mo_loss': -0.355033, 'risk_12mo_loss': 0.108988, 'returns_1': 0.0738, 'cagr_20': 0.0276, 'returns_5': 0.9303}}, 'msa_info': {'msa_name': 'Las Vegas-Henderson-Paradise, NV', 'msa': '29820'}}]
        mock.post("/v2/msa/component_mget", headers=self.headers, json=response)
        self._test_csv_output(self.get_docopt_args(
            'csv', 'msa/*', './sample_input/sample-input-msas.csv'
        ))

    def test_hc_api_export_property_single_endpoint(self, mock):
        response = [{'address_info': {'city': 'Palos Verdes Estates', 'county_fips': '06037', 'geo_precision': 'rooftop', 'block_id': '060376703241005', 'zipcode': '90274', 'address_full': '43 Valmonte Plz Palos Verdes Estates CA 90274', 'zipcode_plus4': '1444', 'state': 'CA', 'metrodiv': '31084', 'unit': None, 'address': '43 Valmonte Plz', 'lat': 33.79814, 'lng': -118.36455, 'slug': '43-Valmonte-Plz-Palos-Verdes-Estates-CA-90274', 'msa': '31080'}, 'property/value': {'api_code_description': 'ok', 'api_code': 0, 'result': {'value': {'price_upr': 1780318, 'price_lwr': 1505350, 'price_mean': 1642834, 'fsd': 0.0836871}}}}]
        mock.post("/v2/property/value", headers=self.headers, json=response)
        self._test_excel_output(self.get_docopt_args(
            'excel', 'property/value', './tests/test_files/test_input.csv'
        ))
