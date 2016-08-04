"""
This module provides an authentication implementation for requests to the HouseCanary API.
"""

import hmac
import hashlib
import datetime
import calendar

try:
    # Python 3
    from urllib.parse import urlencode, urlparse, parse_qsl, urlunparse
except ImportError:
    # Python 2
    from urllib import urlencode
    from urlparse import urlparse, parse_qsl, urlunparse

import requests


class HCAuth(requests.auth.AuthBase):
    """ HouseCanary Authentication handler for Requests."""

    def __init__(self, auth_key, auth_secret):
        """Create an authentication handler for HouseCanary API V1 requests

        Args:
            auth_key (string) - The HouseCanary API auth key
            auth_secret (string) - The HouseCanary API secret
        """

        self._auth_key = auth_key
        self._auth_secret = auth_secret

    def __call__(self, request):
        # Override in subclass
        return request


class HCAuthV1(HCAuth):
    """ HouseCanary API V1 Authentication handler for Requests.

    Generates an HMAC-SHA1 signature for the X-Auth-Signature header.
    """

    SIGN_DELIMITER = "\n"
    AUTH_PROTO_V1 = "hc_hmac_v1"

    def __call__(self, request):
        # parse the url of the request
        scheme, netloc, path, params, query, fragment = urlparse(request.url)

        # convert the query string to a dict
        query_params = dict(parse_qsl(query))

        # add additional query params that are required for authentication
        query_params['AuthKey'] = self._auth_key
        query_params['AuthProto'] = self.AUTH_PROTO_V1
        query_params['AuthTimestamp'] = str(self._get_timestamp_utc())

        # back to string
        query_string = urlencode(query_params, True)

        # get the post data from the request, if any
        data = request.body or ""

        # set the auth signature as required by the HouseCanary API
        signature = self._get_signature(path, query_string, request.method, data)
        request.headers["X-Auth-Signature"] = signature

        # recreate the url with the updated query string
        updated_url = urlunparse([scheme, netloc, path, params, query_string, fragment])
        request.url = requests.utils.requote_uri(updated_url)

        return request

    def _get_signature(self, endpoint_path, query_string, http_method, data):
        # all the inputs should be strings

        # uses hmac to produce a signature from the api secret and a message.
        # The message is defined as:
        # (HTTP_METHOD, HTTP_LOCATION, HTTP_QUERY_STRING, HTTP_POST_BODY)
        # concatenated by newline "\n" (unix style).
        sign_str = self.SIGN_DELIMITER.join([http_method, endpoint_path, query_string, data])
        signature = hmac.new(str(self._auth_secret), sign_str, digestmod=hashlib.sha1).hexdigest()
        return signature

    @staticmethod
    def _get_timestamp_utc():
        cur_utc_time = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
        return cur_utc_time
