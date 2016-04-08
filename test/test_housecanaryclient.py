import unittest
import mock
import json
import os
import housecanary

class TestHouseCanaryClient(unittest.TestCase):
    TEST_API_KEY = "test_key"
    TEST_API_SECRET = "test_secret"

    def setUp(self):
        self.client = housecanary.HouseCanaryClient(self.TEST_API_KEY, self.TEST_API_SECRET)

    def test_init(self):
        self.assertEqual(self.client._version, "v1")
        self.assertEqual(self.client._endpoint_prefix, "/v1/property/")

        del os.environ["HC_API_KEY"]
        del os.environ["HC_API_SECRET"]

        with self.assertRaises(ValueError) as cm:
            housecanary.HouseCanaryClient()
        ex = cm.exception
        self.assertTrue(ex.message.startswith("Missing authentication key."))

        with self.assertRaises(ValueError)as cm:
            housecanary.HouseCanaryClient(self.TEST_API_KEY)
        ex = cm.exception
        self.assertTrue(ex.message.startswith("Missing authentication secret."))

        with self.assertRaises(ValueError) as cm:
            housecanary.HouseCanaryClient(self.TEST_API_KEY, self.TEST_API_SECRET, "v2")
        ex = cm.exception
        self.assertEqual(ex.message, "Only 'v1' is allowed for version.")

    def test_init_with_env_vars(self):
        os.environ["HC_API_KEY"] = self.TEST_API_KEY
        os.environ["HC_API_SECRET"] = self.TEST_API_SECRET

        c = housecanary.HouseCanaryClient()
        self.assertEqual(c._auth_key, self.TEST_API_KEY)
        self.assertEqual(c._auth_secret, self.TEST_API_SECRET)

    def test_get_input_handling(self):
        with self.assertRaises(ValueError) as cm:
            self.client.get("value_report", "1 Main St", "")
        ex = cm.exception
        self.assertEqual(ex.message, "zipcode must be provided if address is provided.")

        with self.assertRaises(ValueError) as cm:
            self.client.get("value_report", "", "01010")
        ex = cm.exception
        self.assertEqual(ex.message, "address must be provided if zipcode is provided.")

    @mock.patch('housecanary.HouseCanaryResponse.create_from_http_response')
    @mock.patch('housecanary.HouseCanaryClient._make_request')
    def test_get(self, make_request, create_response):
        make_request.return_value = "Response"
        create_response.return_value = "HouseCanary Response"

        res = self.client.get("value_report", "1 Main St", "00000")

        query_params = {
            "address": "1 Main St",
            "zipcode": "00000",
            "format": "all",
            "report_type": "full"
        }

        make_request.assert_called_with("/v1/property/value_report", query_params, "GET", None)

        self.assertEqual(res, "HouseCanary Response")

    @mock.patch('housecanary.HouseCanaryResponse.create_from_http_response')
    @mock.patch('housecanary.HouseCanaryClient._make_request')
    def test_get_with_optional_params(self, make_request, create_response):
        make_request.return_value = "Response"
        create_response.return_value = "HouseCanary Response"

        res = self.client.get("value_report", "1 Main St", "00000", "json", "summary")

        query_params = {
            "address": "1 Main St",
            "zipcode": "00000",
            "format": "json",
            "report_type": "summary"
        }

        make_request.assert_called_with("/v1/property/value_report", query_params, "GET", None)

        self.assertEqual(res, "HouseCanary Response")

    @mock.patch('housecanary.HouseCanaryClient._get_post_data_structure')
    @mock.patch('housecanary.HouseCanaryResponse.create_from_http_response')
    @mock.patch('housecanary.HouseCanaryClient._make_request')
    def test_get_multi(self, make_request, create_response, get_data_structure):
        make_request.return_value = "Response"
        create_response.return_value = "HouseCanary Response"
        get_data_structure.return_value = "Data Structure"

        res = self.client.get_multi("value_report",
                                    [["1 Main St", "00000"], ["2 Center St", "11111"]])

        query_params = {
            "format": "all",
            "report_type": "full"
        }

        make_request.assert_called_with("/v1/property/value_report",
                                        query_params, "POST", "Data Structure")

        self.assertEqual(res, "HouseCanary Response")

    @mock.patch('housecanary.HouseCanaryClient._get_post_data_structure')
    @mock.patch('housecanary.HouseCanaryResponse.create_from_http_response')
    @mock.patch('housecanary.HouseCanaryClient._make_request')
    def test_get_multi_with_optional_params(self, make_request,
                                            create_response, get_data_structure):
        make_request.return_value = "Response"
        create_response.return_value = "HouseCanary Response"
        get_data_structure.return_value = "Data Structure"

        res = self.client.get_multi("value_report",
                                    [["1 Main St", "00000"], ["2 Center St", "11111"]],
                                    "json", "summary")

        query_params = {
            "format": "json",
            "report_type": "summary"
        }

        make_request.assert_called_with("/v1/property/value_report",
                                        query_params, "POST", "Data Structure")

        self.assertEqual(res, "HouseCanary Response")

    def test_check_api_param(self):
        allowed_values = ["value_report", "score", "avm"]

        for v in allowed_values:
            self.assertTrue(self.client._check_api_param(v))

        with self.assertRaises(ValueError):
            self.client._check_api_param("wrong")

    def test_get_post_data_structure_error_handling(self):
        with self.assertRaises(ValueError) as cm:
            self.client._get_post_data_structure([])
        ex = cm.exception
        self.assertEqual(ex.message, "You must provide a non-empty address_list.")

        with self.assertRaises(ValueError) as cm:
            self.client._get_post_data_structure("string")
        ex = cm.exception
        self.assertEqual(ex.message, "address_list must be a non-empty list")

    def test_get_post_data_structure_list_of_strings(self):
        res = self.client._get_post_data_structure([["1 Main St", "00000"],
                                                    ["2 Center St", "11111"]])

        self.assertEqual(2, len(res.keys()))

        for k, v in res.iteritems():
            self.assertTrue(v["address"]["address"] in ["1 Main St", "2 Center St"])
            self.assertTrue(v["address"]["zipcode"] in ["00000", "11111"])

    def test_get_post_data_structure_list_of_objects(self):
        addr1 = housecanary.HouseCanaryProperty("1 Main St", "00000", "property_1")
        addr2 = housecanary.HouseCanaryProperty("2 Center St", "11111", "property_2")

        res = self.client._get_post_data_structure([addr1, addr2])

        self.assertEqual(2, len(res.keys()))

        self.assertEqual(res[addr1.unique_id]["address"]["address"], "1 Main St")
        self.assertEqual(res[addr1.unique_id]["address"]["zipcode"], "00000")
        self.assertEqual(res[addr2.unique_id]["address"]["address"], "2 Center St")
        self.assertEqual(res[addr2.unique_id]["address"]["zipcode"], "11111")

    def test_get_post_data_structure_with_invalid_list(self):
        with self.assertRaises(ValueError) as cm:
            self.client._get_post_data_structure(["test1", "test2"])
        ex = cm.exception
        self.assertEqual(ex.message, ("Items in address_list must be lists of strings like "
                                      "[address, zipcode] or HouseCanaryProperty objects."))

    @mock.patch('housecanary.housecanaryclient.urlopen', autospec=True)
    @mock.patch('housecanary.HouseCanaryClient._construct_request')
    def test_make_request(self, construct_request, urlopen):
        urlopen.return_value = "Response"
        construct_request.return_value = "Request"

        self.assertEqual(self.client._make_request("endpoint", "qp", "GET", None), "Response")
        construct_request.assert_called_with("endpoint", "qp", "GET", None)
        urlopen.assert_called_with("Request")

    @mock.patch('housecanary.housecanaryclient.urlopen', autospec=True)
    @mock.patch('housecanary.HouseCanaryClient._construct_request')
    def test_make_request_with_error(self, construct_request, urlopen):
        construct_request.return_value = "Request"
        urlopen.side_effect = ValueError

        with self.assertRaises(ValueError):
            self.client._make_request("endpoint", "qp", "GET", None)

        urlopen.assert_called_with("Request")

    def test_construct_request(self):
        req = self.client._construct_request("/endpoint", {}, "GET", None)

        expected = "https://api.housecanary.com/endpoint?AuthKey=test_key&AuthProto=hc_hmac_v1&AuthTimestamp="
        self.assertTrue(req.get_full_url().startswith(expected))
        self.assertEqual(req.get_method(), "GET")
        self.assertTrue(req.has_header('X-auth-signature'))

    def test_construct_request_with_data(self):
        req = self.client._construct_request("/endpoint", {}, "POST", {"x": "y"})

        expected = "https://api.housecanary.com/endpoint?AuthKey=test_key&AuthProto=hc_hmac_v1&AuthTimestamp="
        self.assertTrue(req.get_full_url().startswith(expected))
        self.assertEqual(req.get_method(), "POST")
        self.assertTrue(req.has_header('X-auth-signature'))
        self.assertTrue(req.has_header('Content-type'))
