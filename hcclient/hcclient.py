#!/usr/bin/env python

import datetime
import calendar
import hmac
import hashlib
import pprint
import json
import os
import uuid

try:
	# Python 3
	from urllib.error import HTTPError
	from urllib.parse import urlencode
	from urllib.request import Request, urlopen
except ImportError:
	# Python 2
	from urllib import urlencode 
	from urllib2 import HTTPError, Request, urlopen

HTTP_STATUS_OK = 200
HTTP_STATUS_FORBIDDEN = 403
HC_BIZ_CODE_OK = 0

class HouseCanaryClient(object):
	"""Encapsulates authentication and methods to call the HouseCanary API."""

	KEY_ENV_VAR = "HC_API_KEY"
	SECRET_ENV_VAR = "HC_API_SECRET"

	PROTO = "hc_hmac_v1"
	SIGN_DELIMITER = "\n"

	URL_PREFIX = "https://api.housecanary.com"

	AVAILABLE_APIS = ["value_report", "score", "avm"]

	def __init__(self, auth_key=None, auth_secret=None):
		"""Initialize the client object for calling the HouseCanary API.

		Args:
			auth_key (optional) -- Your HouseCanary API auth key.
			auth_secret (optional) -- Your HouseCanary API secret.

		Sets up the auth key and secret. These can be passed in as parameters or 
		set via the following environment variables:
			HC_API_KEY -- Your HouseCanary API auth key
			HC_API_SECRET -- Your HouseCanary API secret

		Passing in the key and secret as parameters will take precedence over environment variables.
		"""
		if auth_key is None and self.KEY_ENV_VAR not in os.environ:
			msg = ("Missing authentication key. Either pass it in as the first argument "
				"or set it in the HC_API_KEY environment variable.")
			raise ValueError(msg)

		if auth_secret is None and self.SECRET_ENV_VAR not in os.environ:
			msg = ("Missing authentication secret. Either pass it in as the first argument "
				"or set it in the HC_API_SECRET environment variable.")
			raise ValueError(msg)

		self._auth_key = auth_key or os.environ[self.KEY_ENV_VAR]
		self._auth_secret = auth_secret or os.environ[self.SECRET_ENV_VAR]

	def get(self, api, address, zipcode, format="all", report_type="full"):
		"""Call the HouseCanary Property API with a single address.

		The 'api' param is used to specify which endpoint to call.

		Args:
			api (required) -- The endpoint to call. Can be one of:
				- 'value_report' -- for the Value Report API
				- 'score' -- for the Property Score API
				- 'avm' -- for the Automated Valuation Model API
			address (optional) -- Building number, street name and unit number. Default is None.
				If specified, zipcode must also be specified. 
			zipcode (optional) -- Zipcode that matches the address. Default is None.
				If specified, address must also be specified.
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

		endpoint = "/v1/property/" + api
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
				Default is None.
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

		data_structure = self._get_data_structure_from_args(address_list)

		query_params = {}
		if api == "value_report":
			query_params["format"] = format or "all"
			query_params["report_type"] = report_type or "full"

		endpoint = "/v1/property/" + api
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

	def _get_data_structure_from_args(self, address_list):
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

class HouseCanaryResponse(object):
	"""Encapsulate an http response from the HouseCanary API."""

	def __init__(self, body=None, status_code=None, request_info=None):
		""" Initialize the response object's data.

		Args:
			body (optional) -- The response body string.
			status_code (optional) -- The http status code.
			request_info (optional) -- Details of the request that was made.
		"""
		self._body = body
		self._status_code = status_code
		self._request_info = request_info
		self._hc_properties = []
		self._has_business_error = None
		self._business_error_messages = None

	@classmethod
	def create_from_http_response(cls, http_response, req_info):
		response_body = http_response.read()

		status_code = http_response.getcode()
			
		hc_response = cls(response_body, status_code, req_info)
		return hc_response

	def body(self):
		"""Return the response body string, or None if there was an http error."""
		return self._body

	def body_json(self):
		"""Return the response body as json, or just the body string if it's not valid json."""
		try:
			return json.loads(self._body)
		except (TypeError, ValueError):
			return self._body

	def status_code(self):
		"""Return the http status code."""
		return self._status_code

	def request_info(self):
		"""Return the original request info as json."""
		return self._request_info

	def method(self):
		return self._request_info["method"]

	def get_business_error_messages(self):
		"""Return a list of business error message strings. If there was no error, returns an empty list"""
		if self._business_error_messages is None:
			self._business_error_messages = [{p.unique_id: p.get_business_error()} for p in self.hc_properties() if p.has_business_error()]

		return self._business_error_messages

	def has_business_error(self):
		"""Return true if any requested address had a business logic error, otherwise returns false"""
		if self._has_business_error is None:
			# scan the hc_properties for any business error codes
			self._has_business_error = next((True for p in self.hc_properties() if p.has_business_error()), False)
		return self._has_business_error

	def hc_properties(self):
		"""Return a list of HouseCanaryProperty objects containing their returned data from the API."""
		if not self._hc_properties:
			body_json = self.body_json()
			if not isinstance(body_json, dict):
				return []

			props = []

			if self.method() == "GET":
				# response structure has just one address
				# no unique_id was passed in for this, so just create a random one.
				unique_id = str(uuid.uuid4())
				prop = HouseCanaryProperty.create_from_json(unique_id, body_json)
				props.append(prop)
			else:
				# response structure has multiple addresses with unique_id keys
				for unique_id in body_json.keys():
					prop = HouseCanaryProperty.create_from_json(unique_id, body_json[unique_id])
					props.append(prop)

			self._hc_properties = props
		return self._hc_properties

class HouseCanaryProperty(object):
	"""Encapsulate the representation of a single address"""

	def __init__(self, address, zipcode, unique_id="", data=None, hc_business_error_code=0):
		"""Initialize the HouseCanaryProperty object

		Args:
			address (required) -- Building number, street name and unit number.
			zipcode (required) -- Zipcode that matches the address.
			unique_id (optional) -- A string used in the response from API calls to reference this address. 
				If not specified, unique_id is randomly generated.
			data (optional) -- The data returned from the API for this property. 
				Omit this if you are using this object to call the API.
			hc_business_error_code (optional) -- The HouseCanary business logic error code reflecting any error with this property.
				Omit this if you are using this object to call the API.
		"""

		self.address = str(address)
		self.zipcode = str(zipcode)
		self.unique_id = str(unique_id) or str(uuid.uuid4())
		self.data = data
		self.hc_business_error_code = int(hc_business_error_code)

	@classmethod
	def create_from_json(cls, unique_id, json_data):
		address = None
		zipcode = None
		code = HC_BIZ_CODE_OK
		if "address" in json_data:
			if "address" in json_data["address"]:
				address = json_data["address"]["address"]
			if "zipcode" in json_data["address"]:
				zipcode = json_data["address"]["zipcode"]
		if "code" in json_data:
			code = json_data["code"]

		return cls(address, zipcode, unique_id, json_data, code)

	def has_business_error(self):
		return self.hc_business_error_code > HC_BIZ_CODE_OK

	def get_business_error(self):
		if not self.has_business_error():
			return None
		else:
			if "code_description" in self.data:
				return self.data["code_description"]
			else:
				return None
