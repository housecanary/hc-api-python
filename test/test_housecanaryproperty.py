import unittest
import housecanary

class TestHouseCanaryProperty(unittest.TestCase):
    def test_init(self):
        p = housecanary.HouseCanaryProperty("1 Main St", "00000")
        self.assertEqual(p.address, "1 Main St")
        self.assertEqual(p.zipcode, "00000")
        self.assertIsNotNone(p.unique_id)

    def test_create_from_json(self):
        body = {
            "address": {
                "address": "1 Main St",
                "zipcode": "00000"
            }
        }

        p = housecanary.HouseCanaryProperty.create_from_json("prop_1", body)

        self.assertEqual(p.address, "1 Main St")
        self.assertEqual(p.zipcode, "00000")
        self.assertEqual(p.unique_id, "prop_1")
        self.assertEqual(p.hc_business_error_code, 0)

    def test_create_from_json_with_error(self):
        body = {
            "address": {
                "address": "1 Main St",
                "zipcode": "00000",
            },
            "code": 1001
        }

        p = housecanary.HouseCanaryProperty.create_from_json("prop_1", body)

        self.assertEqual(p.address, "1 Main St")
        self.assertEqual(p.zipcode, "00000")
        self.assertEqual(p.unique_id, "prop_1")
        self.assertEqual(p.hc_business_error_code, 1001)

    def test_has_business_error(self):
        p = housecanary.HouseCanaryProperty("prop_1", "00000")
        p.hc_business_error_code = 1001
        self.assertTrue(p.has_business_error())
        p.hc_business_error_code = 0
        self.assertFalse(p.has_business_error())

    def test_get_business_error(self):
        body = {
            "address": {
                "address": "1 Main St",
                "zipcode": "00000",
            },
            "code": 1001,
            "code_description": "Test error"
        }

        p = housecanary.HouseCanaryProperty.create_from_json("prop_1", body)
        self.assertEqual(p.get_business_error(), "Test error")

    def test_get_business_error_none(self):
        body = {
            "address": {
                "address": "1 Main St",
                "zipcode": "00000",
            },
            "code": 0
        }

        p = housecanary.HouseCanaryProperty.create_from_json("prop_1", body)
        self.assertEqual(p.get_business_error(), None)
