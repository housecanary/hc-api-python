#!/usr/bin/env python

import datetime
import calendar
import hmac
import hashlib
import pprint
import json
import os
from housecanary.housecanaryresponse import HouseCanaryResponse
from housecanary.housecanaryproperty import HouseCanaryProperty

try:
	# Python 3
	from urllib.error import HTTPError
	from urllib.parse import urlencode
	from urllib.request import Request, urlopen
except ImportError:
	# Python 2
	from urllib import urlencode 
	from urllib2 import HTTPError, Request, urlopen

HTTP_STATUS_FORBIDDEN = 403

class HouseCanaryClient(object):
	"""Encapsulates authentication and methods to call the HouseCanary API."""

	KEY_ENV_VAR = "HC_API_KEY"
	SECRET_ENV_VAR = "HC_API_SECRET"

	PROTO = "hc_hmac_v1"
	SIGN_DELIMITER = "\n"

	URL_PREFIX = "https://api.housecanary.com"

	AVAILABLE_APIS = ["value_report", "score", "avm"]

	AVAILABLE_VERSIONS = ["v1"]

	def __init__(self, auth_key=None, auth_secret=None, version="v1"):
		"""Initialize the client object for calling the HouseCanary API.

		Sets up the auth key and secret. These can be passed in as parameters or 
		set via the following environment variables:
			HC_API_KEY -- Your HouseCanary API auth key
			HC_API_SECRET -- Your HouseCanary API secret

		Passing in the key and secret as parameters will take precedence over environment variables.

		:param auth_key: (optional) -- Your HouseCanary API auth key.
		:param auth_secret: (optional) -- Your HouseCanary API secret.
		"""
		if auth_key is None and self.KEY_ENV_VAR not in os.environ:
			msg = ("Missing authentication key. Either pass it in as the first argument "
				"or set it in the HC_API_KEY environment variable.")
			raise ValueError(msg)

		if auth_secret is None and self.SECRET_ENV_VAR not in os.environ:
			msg = ("Missing authentication secret. Either pass it in as the first argument "
				"or set it in the HC_API_SECRET environment variable.")
			raise ValueError(msg)

		if version not in self.AVAILABLE_VERSIONS:
			msg = "Only 'v1' is allowed for version."
			raise ValueError(msg)

		self._auth_key = auth_key or os.environ[self.KEY_ENV_VAR]
		self._auth_secret = auth_secret or os.environ[self.SECRET_ENV_VAR]
		self._version = version
		self._endpoint_prefix = "/" + self._version + "/property/"

	def get(self, api, address, zipcode, format="all", report_type="full"):
		"""Call the HouseCanary Property API with a single address.

		The 'api' param is used to specify which endpoint to call.

		Args:
			api (required) -- The endpoint to call. Can be one of:
				- 'value_report' -- for the Value Report API
				- 'score' -- for the Property Score API
				- 'avm' -- for the Automated Valuation Model API
			address (required) -- Building number, street name and unit number.
			zipcode (required) -- Zipcode that matches the address.
			format (optional) -- Output format. Can be 'json', 'pdf' or 'all'. 
				The default is 'all', which is a zip of all available formats.
				format is only used when api is set to 'value_report'
			report_type (optional) -- Type of report. Can be 'summary' or 'full'. The default is 'full'.
				report_type is only used when api is set to 'value_report'

		Raises ValueError if:
			- 'api' is not one of 'value_report', 'score' or 'avm'
			- one of 'address' and 'zipcode' is not provided 

		Returns a HouseCanaryResponse object.
		"""

		api = api.lower()
		self._check_api_param(api)

		if zipcode and not address:
			raise ValueError("address must be provided if zipcode is provided.")
		
		if address and not zipcode:
			raise ValueError("zipcode must be provided if address is provided.")

		query_params = {
			"address": address,
			"zipcode": zipcode
		}

		if api == "value_report":
			query_params["format"] = format or "all"
			query_params["report_type"] = report_type or "full"

		endpoint = self._endpoint_prefix + api
		method = "GET"
		data = None

		response = self._make_request(endpoint, query_params, method, data)

		req_info = {
			"endpoint": endpoint,
			"method": method,
			"params": query_params,
			"data": None
		}

		return HouseCanaryResponse.create_from_http_response(response, req_info)


	def get_multi(self, api, address_list, format="all", report_type="full"):
		"""Call the HouseCanary Property API with multiple addresses in batch. 

		The 'api' param is used to specify which endpoint to call.

		Args:
			api (required) -- The endpoint to call. Can be one of:
				- 'value_report' -- for the Value Report API
				- 'score' -- for the Property Score API
				- 'avm' -- for the Automated Valuation Model API
			address_list (required) -- A list used for calling the API with multiple addresses.
				Can be one of:
					- A two dimensional list of address and zipcode strings
						Example: [['700 Boylston St', '02116'], ['201 Spear St', '94105']]		
					- A list of HouseCanaryProperty objects
			format (optional) -- Output format. Can be 'json', 'pdf' or 'all'. 
				The default is 'all', which is a zip of all available formats.
				format is only used when api is set to 'value_report'
			report_type (optional) -- Type of report. Can be 'summary' or 'full'. The default is 'full'.
				report_type is only used when api is set to 'value_report'

		Raises ValueError if:
			- 'api' is not one of 'value_report', 'score' or 'avm'
			- 'address_list' is not a list of the proper form (see Args above.)

		Returns a HouseCanaryResponse object.
		"""

		api = api.lower()
		self._check_api_param(api)

		data_structure = self._get_post_data_structure_from_args(address_list)

		query_params = {}
		if api == "value_report":
			query_params["format"] = format or "all"
			query_params["report_type"] = report_type or "full"

		endpoint = self._endpoint_prefix + api
		method = "POST"

		response = self._make_request(endpoint, query_params, method, data_structure)

		req_info = {
			"endpoint": endpoint,
			"method": method,
			"params": query_params,
			"data": data_structure
		}

		return HouseCanaryResponse.create_from_http_response(response, req_info)

	def _check_api_param(self, api):
		if api.lower() not in self.AVAILABLE_APIS:
			raise ValueError("api param is invalid. It must be one of " + ", ".join(self.AVAILABLE_APIS))
		return True

	def _get_post_data_structure_from_args(self, address_list):
		if not address_list:
			raise ValueError("You must provide a non-empty address_list.")

		if not isinstance(address_list, list):
			raise ValueError("address_list must be a non-empty list")

		data_structure = {}
		
		for i, v in enumerate(address_list):
			if isinstance(v, HouseCanaryProperty):
				hc_address = v
			elif isinstance(v, list):
				hc_address = HouseCanaryProperty(v[0], v[1])
			else:
				raise ValueError("Items in address_list must be lists of strings like [address, zipcode] or HouseCanaryProperty objects.")

			data_structure[hc_address.unique_id] = {
				"address": {
					"address": hc_address.address,
					"zipcode": hc_address.zipcode
				}
			}

		return data_structure

	def _make_request(self, endpoint, query_params, method, data):
		req = self._construct_request(endpoint, query_params, method, data)
		try:
			response = urlopen(req)
			return response
		except HTTPError, e:
			error_json = json.loads(e.read())

			if e.getcode() == HTTP_STATUS_FORBIDDEN:
				e.msg = "You are not authenticated. " + e.msg
			elif "message" in error_json:
				# message contains custom error messages from the API
				message = error_json["message"]
				
				# multiple error messages come back as json
				error_messages = []
				if isinstance(message, dict):
					for key in message.keys():
						error_messages.append(key + ": " + message[key])
				else:
					error_messages = [message]

				e.msg = ". ".join(error_messages) + ". " + e.msg
			raise 

	def _construct_request(self, endpoint, query_params, method, data=None):
		if data:
			data = json.dumps(data)

		query_params['AuthKey'] = self._auth_key
		query_params['AuthProto'] = self.PROTO
		query_params['AuthTimestamp'] = str(self._get_timestamp_utc())
		query_string = urlencode(query_params, True)

		url = self.URL_PREFIX + endpoint + "?" + query_string

		req = Request(url, data)

		signature = self._get_signature(endpoint, query_string, method, data)
		req.add_header("X-Auth-Signature", signature)
		if data:
			req.add_header('Content-Type', 'application/json')

		return req

	def _get_timestamp_utc(self):
		cur_utc_time = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
		return cur_utc_time

	def _get_signature(self, endpoint, query_string, method, data):
		sign_str = self.SIGN_DELIMITER.join([method, endpoint, query_string, data or ""])
		signature = hmac.new(str(self._auth_secret), sign_str, digestmod=hashlib.sha1).hexdigest()
		return signature
