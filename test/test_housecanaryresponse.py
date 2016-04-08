import unittest
import housecanary
import mock
import json

class TestHouseCanaryResponse(unittest.TestCase):
    def test_init(self):
        r = housecanary.HouseCanaryResponse("Body", 200, "Req Info")
        self.assertEqual(r.body(), "Body")
        self.assertEqual(r.status_code(), 200)
        self.assertEqual(r.request_info(), "Req Info")

    def test_create_from_http_response(self):
        http_response = mock.MagicMock()
        http_response.read.return_value = "Response body"
        http_response.getcode.return_value = 200

        r = housecanary.HouseCanaryResponse.create_from_http_response(http_response, "req info")

        self.assertEqual(r.body(), "Response body")
        self.assertEqual(r.status_code(), 200)

    def test_body_json(self):
        r = housecanary.HouseCanaryResponse("Body", 200, "Req Info")
        self.assertEqual(r.body_json(), "Body")

        body = {"address": "test"}
        r = housecanary.HouseCanaryResponse(json.dumps(body), 200, "Req Info")
        self.assertEqual(r.body_json(), body)

    def test_hc_properties_with_get(self):
        body = {
            "address": {
                "address": "1 Main St",
                "zipcode": "00000"
            }
        }

        request_info = {
            "method": "GET"
        }

        r = housecanary.HouseCanaryResponse(body, 200, request_info)
        self.assertEqual(len(r.hc_properties()), 1)
        prop = r.hc_properties()[0]
        self.assertEqual(prop.address, "1 Main St")
        self.assertEqual(prop.zipcode, "00000")
        self.assertEqual(prop.data, body)

    def test_hc_properties_with_post(self):
        body = {
            "property_1": {
                "address": {
                    "address": "1 Main St",
                    "zipcode": "00000"
                }
            },
            "property_2": {
                "address": {
                    "address": "2 Center St",
                    "zipcode": "11111"
                }
            }
        }

        request_info = {
            "method": "POST"
        }

        r = housecanary.HouseCanaryResponse(body, 200, request_info)
        self.assertEqual(len(r.hc_properties()), 2)

        prop1 = next(p for p in r.hc_properties() if p.unique_id == "property_1")
        self.assertEqual(prop1.address, "1 Main St")
        self.assertEqual(prop1.zipcode, "00000")

        prop2 = next(p for p in r.hc_properties() if p.unique_id == "property_2")
        self.assertEqual(prop2.address, "2 Center St")
        self.assertEqual(prop2.zipcode, "11111")

    def test_hc_properties_with_bad_body(self):
        body = "Bad body"

        request_info = {
            "method": "POST"
        }

        r = housecanary.HouseCanaryResponse(body, 200, request_info)
        self.assertEqual(r.hc_properties(), [])

    def test_has_business_error_with_one(self):
        request_info = {
            "method": "POST"
        }
        r = housecanary.HouseCanaryResponse("", 200, request_info)
        r._hc_properties = [housecanary.HouseCanaryProperty("1 Main St", "00000", "prop_1", None, 1001)]
        self.assertTrue(r.has_business_error())

    def test_has_business_error_with_many(self):
        request_info = {
            "method": "POST"
        }
        r = housecanary.HouseCanaryResponse("", 200, request_info)
        p1 = housecanary.HouseCanaryProperty("1 Main St", "00000", "prop_1", None, 1001)
        p2 = housecanary.HouseCanaryProperty("2 Main St", "00000", "prop_2", None, 0)
        p3 = housecanary.HouseCanaryProperty("3 Main St", "00000", "prop_3", None, 0)
        r._hc_properties = [p1, p2, p3]
        self.assertTrue(r.has_business_error())

    def test_has_business_error_with_false(self):
        request_info = {
            "method": "POST"
        }
        r = housecanary.HouseCanaryResponse("", 200, request_info)
        p1 = housecanary.HouseCanaryProperty("1 Main St", "00000", "prop_1", None, 0)
        p2 = housecanary.HouseCanaryProperty("2 Main St", "00000", "prop_2", None, 0)
        p3 = housecanary.HouseCanaryProperty("3 Main St", "00000", "prop_3", None, 0)
        r._hc_properties = [p1, p2, p3]
        self.assertFalse(r.has_business_error())

    def test_has_business_error_with_no_props(self):
        request_info = {
            "method": "POST"
        }
        r = housecanary.HouseCanaryResponse("", 200, request_info)
        r._hc_properties = []
        self.assertFalse(r.has_business_error())

    def test_get_business_error_messages(self):
        request_info = {
            "method": "POST"
        }
        r = housecanary.HouseCanaryResponse("", 200, request_info)
        data = {"code_description": "Test error"}
        p1 = housecanary.HouseCanaryProperty("1 Main St", "00000", "prop_1", data, 1001)
        p2 = housecanary.HouseCanaryProperty("2 Main St", "00000", "prop_2", None, 0)
        p3 = housecanary.HouseCanaryProperty("3 Main St", "00000", "prop_3", None, 0)
        r._hc_properties = [p1, p2, p3]
        self.assertEqual(r.get_business_error_messages(), [{"prop_1": "Test error"}])

    def test_get_business_error_messages_with_no_error(self):
        request_info = {
            "method": "POST"
        }
        r = housecanary.HouseCanaryResponse("", 200, request_info)
        p1 = housecanary.HouseCanaryProperty("1 Main St", "00000", "prop_1", None, 0)
        p2 = housecanary.HouseCanaryProperty("2 Main St", "00000", "prop_2", None, 0)
        p3 = housecanary.HouseCanaryProperty("3 Main St", "00000", "prop_3", None, 0)
        r._hc_properties = [p1, p2, p3]
        self.assertEqual(r.get_business_error_messages(), [])

    def test_get_business_error_messages_with_no_properties(self):
        request_info = {
            "method": "POST"
        }
        r = housecanary.HouseCanaryResponse("", 200, request_info)
        r._hc_properties = []
        self.assertEqual(r.get_business_error_messages(), [])
