"""
These tests require the HC_API_KEY and HC_API_SECRET environment variables to be set.
"""

# pylint: disable=missing-docstring

import unittest
from housecanary.object import Property
from housecanary.object import Block
from housecanary.object import ZipCode


class PropertyTestCase(unittest.TestCase):
    def setUp(self):
        self.test_json = {
            'property/value': {
                'api_code_description': 'ok',
                'api_code': 0,
                'result': {
                    'price_pr': 2938.0, 'price_lwr': 2160.0, 'price_mean': 2296.0, 'fsd': 0.17
                }
            },
            'address_info': {
                'city': 'Peabody', 'county_fips': '25009', 'zipcode': '01960',
                'address_full': '47 Perley Ave Peabody MA 01960', 'state': 'MA',
                'zipcode_plus4': '3459', 'address': '47 Perley Ave',
                'lat': 42.549, 'lng': -71.029, 'unit': None
            },
            'meta': 'Test Meta'
        }

        self.prop = Property.create_from_json(self.test_json)

    def test_create_from_json(self):
        self.assertEqual(self.prop.address, "47 Perley Ave")
        self.assertEqual(self.prop.county_fips, "25009")
        self.assertEqual(self.prop.zipcode, "01960")
        self.assertEqual(self.prop.address_full, "47 Perley Ave Peabody MA 01960")
        self.assertEqual(self.prop.state, "MA")
        self.assertEqual(self.prop.zipcode_plus4, "3459")
        self.assertEqual(self.prop.city, "Peabody")
        self.assertEqual(self.prop.lat, 42.549)
        self.assertEqual(self.prop.lng, -71.029)
        self.assertEqual(self.prop.unit, None)
        self.assertEqual(self.prop.meta, 'Test Meta')
        self.assertEqual(len(self.prop.component_results), 1)
        self.assertEqual(self.prop.component_results[0].api_code, 0)
        self.assertEqual(self.prop.component_results[0].api_code_description, 'ok')
        self.assertEqual(self.prop.component_results[0].json_data, {
            'price_pr': 2938.0, 'price_lwr': 2160.0, 'price_mean': 2296.0, 'fsd': 0.17
        })

    def test_create_from_json_with_multiple_components(self):
        test_json2 = {
            'property/value': {
                'api_code_description': 'ok',
                'api_code': 0,
                'result': {
                    'price_pr': 2938.0, 'price_lwr': 2160.0, 'price_mean': 2296.0, 'fsd': 0.17
                }
            },
            'property/census': {
                'api_code_description': 'ok',
                'api_code': 0,
                'result': 'dummy data'
            },
            'address_info': {
                'city': 'Peabody', 'county_fips': '25009', 'zipcode': '01960',
                'address_full': '47 Perley Ave Peabody MA 01960', 'state': 'MA',
                'zipcode_plus4': '3459', 'address': '47 Perley Ave',
                'lat': 42.549, 'lng': -71.029, 'unit': None
            },
            'meta': 'Test Meta'
        }

        prop2 = Property.create_from_json(test_json2)

        self.assertEqual(prop2.address, "47 Perley Ave")
        self.assertEqual(len(prop2.component_results), 2)
        value_result = next(
            (cr for cr in prop2.component_results if cr.component_name == "property/value"),
            None
        )
        self.assertIsNotNone(value_result)
        census_result = next(
            (cr for cr in prop2.component_results if cr.component_name == "property/census"),
            None
        )
        self.assertEqual(census_result.json_data, "dummy data")

    def test_has_error(self):
        self.assertFalse(self.prop.has_error())

    def test_has_error_with_error(self):
        self.test_json['property/value']['api_code'] = 1001
        prop2 = Property.create_from_json(self.test_json)
        self.assertTrue(prop2.has_error())

    def test_get_errors(self):
        self.assertEqual(self.prop.get_errors(), [])

    def test_get_errors_with_errors(self):
        self.test_json['property/value']['api_code'] = 1001
        self.test_json['property/value']['api_code_description'] = "test error"
        prop2 = Property.create_from_json(self.test_json)
        self.assertEqual(prop2.get_errors(), [{"property/value": "test error"}])


class BlockTestCase(unittest.TestCase):
    def setUp(self):
        self.test_json = {
            'block/value_ts': {
                'api_code_description': 'ok',
                'api_code': 0,
                'result': {
                    'value_sqft_median': 303.36
                }
            },
            'block_info': {
                'property_type': 'SFD',
                'block_id': '060376703241005'
            },
            'meta': 'Test Meta'
        }

        self.block = Block.create_from_json(self.test_json)

    def test_create_from_json(self):
        self.assertEqual(self.block.block_id, "060376703241005")
        self.assertEqual(self.block.property_type, "SFD")
        self.assertEqual(self.block.num_bins, None)
        self.assertEqual(self.block.meta, "Test Meta")
        self.assertEqual(len(self.block.component_results), 1)
        self.assertEqual(self.block.component_results[0].api_code, 0)
        self.assertEqual(self.block.component_results[0].api_code_description, 'ok')
        self.assertEqual(self.block.component_results[0].json_data, {'value_sqft_median': 303.36})

    def test_create_from_json_with_num_bins(self):
        json = self.test_json.copy()
        json["block_info"] = {
            "block_id": "060376703241005",
            "num_bins": "5"
        }
        self.block = Block.create_from_json(json)
        self.assertEqual(self.block.block_id, "060376703241005")
        self.assertEqual(self.block.property_type, None)
        self.assertEqual(self.block.num_bins, "5")

    def test_create_from_json_with_multiple_components(self):
        test_json2 = {
            'block/value_ts': {
                'api_code_description': 'ok',
                'api_code': 0,
                'result': {
                    'value_sqft_median': 303.36
                }
            },
            'block/histogram_beds': {
                'api_code_description': 'ok',
                'api_code': 0,
                'result': 'dummy data'
            },
            'block_info': {
                'property_type': 'SFD',
                'block_id': '060376703241005'
            },
            'meta': 'Test Meta'
        }

        block2 = Block.create_from_json(test_json2)

        self.assertEqual(block2.block_id, "060376703241005")
        self.assertEqual(len(block2.component_results), 2)
        result1 = next(
            (cr for cr in block2.component_results if cr.component_name == "block/value_ts"),
            None
        )
        self.assertIsNotNone(result1)
        result2 = next(
            (cr for cr in block2.component_results if cr.component_name == "block/histogram_beds"),
            None
        )
        self.assertEqual(result2.json_data, "dummy data")

    def test_has_error(self):
        self.assertFalse(self.block.has_error())

    def test_has_error_with_error(self):
        self.test_json['block/value_ts']['api_code'] = 1001
        block2 = Block.create_from_json(self.test_json)
        self.assertTrue(block2.has_error())

    def test_get_errors(self):
        self.assertEqual(self.block.get_errors(), [])

    def test_get_errors_with_errors(self):
        self.test_json['block/value_ts']['api_code'] = 1001
        self.test_json['block/value_ts']['api_code_description'] = "test error"
        block2 = Block.create_from_json(self.test_json)
        self.assertEqual(block2.get_errors(), [{"block/value_ts": "test error"}])


class ZipTestCase(unittest.TestCase):
    def setUp(self):
        self.test_json = {
            'zip/details': {
                'api_code_description': 'ok',
                'api_code': 0,
                'result': 'some result'
            },
            'zipcode_info': {
                'zipcode': '90274'
            },
            'meta': 'Test Meta'
        }

        self.zip = ZipCode.create_from_json(self.test_json)

    def test_create_from_json(self):
        self.assertEqual(self.zip.zipcode, "90274")
        self.assertEqual(self.zip.meta, "Test Meta")
        self.assertEqual(len(self.zip.component_results), 1)
        self.assertEqual(self.zip.component_results[0].api_code, 0)
        self.assertEqual(self.zip.component_results[0].api_code_description, 'ok')
        self.assertEqual(self.zip.component_results[0].json_data, 'some result')

    def test_create_from_json_with_multiple_components(self):
        test_json2 = {
            'zip/details': {
                'api_code_description': 'ok',
                'api_code': 0,
                'result': 'details result'
            },
            'zip/volatility': {
                'api_code_description': 'ok',
                'api_code': 0,
                'result': 'dummy data'
            },
            'zipcode_info': {
                'zipcode': '90274',
            },
            'meta': 'Test Meta'
        }

        zip2 = ZipCode.create_from_json(test_json2)

        self.assertEqual(zip2.zipcode, "90274")
        self.assertEqual(len(zip2.component_results), 2)
        result1 = next(
            (cr for cr in zip2.component_results if cr.component_name == "zip/details"),
            None
        )
        self.assertEqual(result1.json_data, "details result")
        result2 = next(
            (cr for cr in zip2.component_results if cr.component_name == "zip/volatility"),
            None
        )
        self.assertEqual(result2.json_data, "dummy data")

    def test_has_error(self):
        self.assertFalse(self.zip.has_error())

    def test_has_error_with_error(self):
        self.test_json['zip/details']['api_code'] = 1001
        zip2 = ZipCode.create_from_json(self.test_json)
        self.assertTrue(zip2.has_error())

    def test_get_errors(self):
        self.assertEqual(self.zip.get_errors(), [])

    def test_get_errors_with_errors(self):
        self.test_json['zip/details']['api_code'] = 1001
        self.test_json['zip/details']['api_code_description'] = "test error"
        zip2 = ZipCode.create_from_json(self.test_json)
        self.assertEqual(zip2.get_errors(), [{"zip/details": "test error"}])


if __name__ == "__main__":
    unittest.main()
