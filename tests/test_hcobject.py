"""
These tests require the HC_API_KEY and HC_API_SECRET environment variables to be set.
"""

# pylint: disable=missing-docstring

import unittest
from housecanary.hcobject import HouseCanaryAddress

class HouseCanaryAddressTestCase(unittest.TestCase):
    def setUp(self):
        self.test_json = {
            'property/rental_value': {
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

        self.prop = HouseCanaryAddress.create_from_json("property/rental_value", self.test_json)

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
        self.assertEqual(self.prop.api_code, 0)
        self.assertEqual(self.prop.api_code_description, 'ok')
        self.assertEqual(self.prop.json_results, {
            'price_pr': 2938.0, 'price_lwr': 2160.0, 'price_mean': 2296.0, 'fsd': 0.17
        })

    def test_has_error(self):
        self.assertFalse(self.prop.has_error())

    def test_has_error_with_error(self):
        self.test_json['property/rental_value']['api_code'] = 1001
        prop2 = HouseCanaryAddress.create_from_json("property/rental_value", self.test_json)
        self.assertTrue(prop2.has_error())

    def test_get_error(self):
        self.assertEqual(self.prop.get_error(), 'ok')

if __name__ == "__main__":
    unittest.main()
