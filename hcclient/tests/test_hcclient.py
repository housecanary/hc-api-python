import unittest
import mock
import json
import os
import hcclient

class TestHouseCanaryClient(unittest.TestCase):
	TEST_API_KEY = "test_key"
	TEST_API_SECRET = "test_secret"

	def setUp(self):
		self.client = hcclient.HouseCanaryClient(self.TEST_API_KEY, self.TEST_API_SECRET)

	def test_init(self):
		del os.environ["HC_API_KEY"]
		del os.environ["HC_API_SECRET"]

		with self.assertRaises(ValueError):
			c = hcclient.HouseCanaryClient()

		with self.assertRaises(ValueError):
			c = hcclient.HouseCanaryClient(self.TEST_API_KEY)

	def test_init_with_env_vars(self):
		os.environ["HC_API_KEY"] = self.TEST_API_KEY
		os.environ["HC_API_SECRET"] = self.TEST_API_SECRET

		c = hcclient.HouseCanaryClient()
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

	@mock.patch('hcclient.HouseCanaryResponse.create_from_http_response')
	@mock.patch('hcclient.HouseCanaryClient._make_request')
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

	@mock.patch('hcclient.HouseCanaryResponse.create_from_http_response')
	@mock.patch('hcclient.HouseCanaryClient._make_request')
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

	@mock.patch('hcclient.HouseCanaryClient._get_data_structure_from_args')
	@mock.patch('hcclient.HouseCanaryResponse.create_from_http_response')
	@mock.patch('hcclient.HouseCanaryClient._make_request')
	def test_get_multi(self, make_request, create_response, get_data_structure):
		make_request.return_value = "Response"
		create_response.return_value = "HouseCanary Response"
		get_data_structure.return_value = "Data Structure"

		res = self.client.get_multi("value_report", [["1 Main St", "00000"], ["2 Center St", "11111"]])

		query_params = {
			"format": "all",
			"report_type": "full"
		}

		make_request.assert_called_with("/v1/property/value_report", query_params, "POST", "Data Structure")

		self.assertEqual(res, "HouseCanary Response")

	@mock.patch('hcclient.HouseCanaryClient._get_data_structure_from_args')
	@mock.patch('hcclient.HouseCanaryResponse.create_from_http_response')
	@mock.patch('hcclient.HouseCanaryClient._make_request')
	def test_get_multi_with_optional_params(self, make_request, create_response, get_data_structure):
		make_request.return_value = "Response"
		create_response.return_value = "HouseCanary Response"
		get_data_structure.return_value = "Data Structure"

		res = self.client.get_multi("value_report", [["1 Main St", "00000"], ["2 Center St", "11111"]], "json", "summary")

		query_params = {
			"format": "json",
			"report_type": "summary"
		}

		make_request.assert_called_with("/v1/property/value_report", query_params, "POST", "Data Structure")

		self.assertEqual(res, "HouseCanary Response")

	def test_check_api_param(self):
		allowed_values = ["value_report", "score", "avm"]

		for v in allowed_values:
			self.assertTrue(self.client._check_api_param(v))

		with self.assertRaises(ValueError):
			self.client._check_api_param("wrong")

	def test_get_data_structure_from_args_error_handling(self):
		with self.assertRaises(ValueError) as cm:
			self.client._get_data_structure_from_args([])
		ex = cm.exception
		self.assertEqual(ex.message, "You must provide a non-empty address_list.")

		with self.assertRaises(ValueError) as cm:
			self.client._get_data_structure_from_args("string")
		ex = cm.exception
		self.assertEqual(ex.message, "address_list must be a non-empty list")

	def test_get_data_structure_from_args_list_of_strings(self):
		res = self.client._get_data_structure_from_args([["1 Main St", "00000"], ["2 Center St", "11111"]])

		self.assertEqual(2, len(res.keys()))

		for k, v in res.iteritems():
			self.assertTrue(v["address"]["address"] in ["1 Main St", "2 Center St"])
			self.assertTrue(v["address"]["zipcode"] in ["00000", "11111"])

	def test_get_data_structure_from_args_list_of_objects(self):
		addr1 = hcclient.HouseCanaryProperty("1 Main St", "00000", "property_1")
		addr2 = hcclient.HouseCanaryProperty("2 Center St", "11111", "property_2")

		res = self.client._get_data_structure_from_args([addr1, addr2])

		self.assertEqual(2, len(res.keys()))

		self.assertEqual(res[addr1.unique_id]["address"]["address"], "1 Main St")
		self.assertEqual(res[addr1.unique_id]["address"]["zipcode"], "00000")
		self.assertEqual(res[addr2.unique_id]["address"]["address"], "2 Center St")
		self.assertEqual(res[addr2.unique_id]["address"]["zipcode"], "11111")

	@mock.patch('hcclient.hcclient.urlopen', autospec=True)
	@mock.patch('hcclient.HouseCanaryClient._construct_request')
	def test_make_request(self, construct_request, urlopen):
		urlopen.return_value = "Response"
		construct_request.return_value = "Request"

		self.assertEqual(self.client._make_request("endpoint", "qp", "GET", None), "Response")
		construct_request.assert_called_with("endpoint", "qp", "GET", None)
		urlopen.assert_called_with("Request")

	@mock.patch('hcclient.hcclient.urlopen', autospec=True)
	@mock.patch('hcclient.HouseCanaryClient._construct_request')
	def test_make_request_with_error(self, construct_request, urlopen):
		construct_request.return_value = "Request"
		urlopen.side_effect = ValueError

		with self.assertRaises(ValueError):
			self.client._make_request("endpoint", "qp", "GET", None)

		urlopen.assert_called_with("Request")

	def test_construct_request(self):
		req = self.client._construct_request("/endpoint", {}, "GET", None)

		self.assertTrue(req.get_full_url().startswith('https://api.housecanary.com/endpoint?AuthKey=test_key&AuthProto=hc_hmac_v1&AuthTimestamp='))
		self.assertEqual(req.get_method(), "GET")
		self.assertTrue(req.has_header('X-auth-signature'))

	def test_construct_request_with_data(self):
		req = self.client._construct_request("/endpoint", {}, "POST", {"x": "y"})

		self.assertTrue(req.get_full_url().startswith('https://api.housecanary.com/endpoint?AuthKey=test_key&AuthProto=hc_hmac_v1&AuthTimestamp='))
		self.assertEqual(req.get_method(), "POST")
		self.assertTrue(req.has_header('X-auth-signature'))
		self.assertTrue(req.has_header('Content-type'))

class TestHouseCanaryResponse(unittest.TestCase):
	def test_init(self):
		r = hcclient.HouseCanaryResponse("Body", 200, "Req Info")
		self.assertEqual(r.body(), "Body")
		self.assertEqual(r.status_code(), 200)
		self.assertEqual(r.request_info(), "Req Info")

	def test_create_from_http_response(self):
		http_response = mock.MagicMock()
		http_response.read.return_value = "Response body"
		http_response.getcode.return_value = 200

		r = hcclient.HouseCanaryResponse.create_from_http_response(http_response, "req info")

		self.assertEqual(r.body(), "Response body")
		self.assertEqual(r.status_code(), 200)

	def test_body_json(self):
		r = hcclient.HouseCanaryResponse("Body", 200, "Req Info")
		self.assertEqual(r.body_json(), "Body")

		body = {"address": "test"}
		r = hcclient.HouseCanaryResponse(json.dumps(body), 200, "Req Info")
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

		r = hcclient.HouseCanaryResponse(body, 200, request_info)
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

		r = hcclient.HouseCanaryResponse(body, 200, request_info)
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

		r = hcclient.HouseCanaryResponse(body, 200, request_info)
		self.assertEqual(r.hc_properties(), [])

	def test_has_business_error_with_one(self):
		request_info = {
			"method": "POST"
		}
		r = hcclient.HouseCanaryResponse("", 200, request_info)
		r._hc_properties = [hcclient.HouseCanaryProperty("1 Main St", "00000", "prop_1", None, 1001)]
		self.assertTrue(r.has_business_error())

	def test_has_business_error_with_many(self):
		request_info = {
			"method": "POST"
		}
		r = hcclient.HouseCanaryResponse("", 200, request_info)
		p1 = hcclient.HouseCanaryProperty("1 Main St", "00000", "prop_1", None, 1001)
		p2 = hcclient.HouseCanaryProperty("2 Main St", "00000", "prop_2", None, 0)
		p3 = hcclient.HouseCanaryProperty("3 Main St", "00000", "prop_3", None, 0)
		r._hc_properties = [p1, p2, p3]
		self.assertTrue(r.has_business_error())

	def test_has_business_error_with_false(self):
		request_info = {
			"method": "POST"
		}
		r = hcclient.HouseCanaryResponse("", 200, request_info)
		p1 = hcclient.HouseCanaryProperty("1 Main St", "00000", "prop_1", None, 0)
		p2 = hcclient.HouseCanaryProperty("2 Main St", "00000", "prop_2", None, 0)
		p3 = hcclient.HouseCanaryProperty("3 Main St", "00000", "prop_3", None, 0)
		r._hc_properties = [p1, p2, p3]
		self.assertFalse(r.has_business_error())

	def test_has_business_error_with_no_props(self):
		request_info = {
			"method": "POST"
		}
		r = hcclient.HouseCanaryResponse("", 200, request_info)
		r._hc_properties = []
		self.assertFalse(r.has_business_error())

	def test_get_business_error_messages(self):
		request_info = {
			"method": "POST"
		}
		r = hcclient.HouseCanaryResponse("", 200, request_info)
		data = {"code_description": "Test error"}
		p1 = hcclient.HouseCanaryProperty("1 Main St", "00000", "prop_1", data, 1001)
		p2 = hcclient.HouseCanaryProperty("2 Main St", "00000", "prop_2", None, 0)
		p3 = hcclient.HouseCanaryProperty("3 Main St", "00000", "prop_3", None, 0)
		r._hc_properties = [p1, p2, p3]
		self.assertEqual(r.get_business_error_messages(), [{"prop_1": "Test error"}])

	def test_get_business_error_messages_with_no_error(self):
		request_info = {
			"method": "POST"
		}
		r = hcclient.HouseCanaryResponse("", 200, request_info)
		p1 = hcclient.HouseCanaryProperty("1 Main St", "00000", "prop_1", None, 0)
		p2 = hcclient.HouseCanaryProperty("2 Main St", "00000", "prop_2", None, 0)
		p3 = hcclient.HouseCanaryProperty("3 Main St", "00000", "prop_3", None, 0)
		r._hc_properties = [p1, p2, p3]
		self.assertEqual(r.get_business_error_messages(), [])

	def test_get_business_error_messages_with_no_properties(self):
		request_info = {
			"method": "POST"
		}
		r = hcclient.HouseCanaryResponse("", 200, request_info)
		r._hc_properties = []
		self.assertEqual(r.get_business_error_messages(), [])

class TestHouseCanaryProperty(unittest.TestCase):
	def test_init(self):
		p = hcclient.HouseCanaryProperty("1 Main St", "00000")
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

		p = hcclient.HouseCanaryProperty.create_from_json("prop_1", body)

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

		p = hcclient.HouseCanaryProperty.create_from_json("prop_1", body)

		self.assertEqual(p.address, "1 Main St")
		self.assertEqual(p.zipcode, "00000")
		self.assertEqual(p.unique_id, "prop_1")
		self.assertEqual(p.hc_business_error_code, 1001)

	def test_has_business_error(self):
		p = hcclient.HouseCanaryProperty("prop_1", "00000")
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

		p = hcclient.HouseCanaryProperty.create_from_json("prop_1", body)
		self.assertEqual(p.get_business_error(), "Test error")

	def test_get_business_error_none(self):
		body = {
			"address": {
				"address": "1 Main St",
				"zipcode": "00000",
			},
			"code": 0
		}

		p = hcclient.HouseCanaryProperty.create_from_json("prop_1", body)
		self.assertEqual(p.get_business_error(), None)
