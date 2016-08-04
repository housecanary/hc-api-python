"""
Provides a base client for making API requests.
"""

import requests


class RequestClient(object):
    """Base class for making http requests with the 'requests' lib."""

    def __init__(self, output_generator=None, authenticator=None):
        """
        Args:
            output_generator - Optional. An instance of an OutputGenerator that implements
                               a `process_response` method. Can be used to implement custom
                               serialization of the response data from the `execute_request`
                               method. If not specified, `execute_request` returns the
                               response from the requests lib unchanged.
            authenticator - Optional. An instance of a requests.auth.AuthBase implementation
                            for providing authentication to the request.
        """
        self._output_generator = output_generator
        self._auth = authenticator

    def execute_request(self, url, http_method, query_params, post_data):
        """Makes a request to the specified url endpoint with the
        specified http method, params and post data.

        Args:
            url (string): The url to the API without query params.
                          Example: "https://api.housecanary.com/v2/property/value"
            http_method (string): The http method to use for the request.
            query_params (dict): Dictionary of query params to add to the request.
            post_data: Json post data to send in the body of the request.

        Returns:
            The result of calling this instance's OutputGenerator process_response method
            on the requests.Response object.
            If no OutputGenerator is specified for this instance, returns the requests.Response.
        """

        response = requests.request(http_method, url, params=query_params,
                                    auth=self._auth, json=post_data)

        if isinstance(self._output_generator, str) and self._output_generator.lower() == "json":
            # shortcut for just getting json back
            return response.json()
        elif self._output_generator is not None:
            return self._output_generator.process_response(response)
        else:
            return response

    def get(self, url, query_params):
        """Makes a GET request to the specified url endpoint.

        Args:
            url (string): The url to the API without query params.
                          Example: "https://api.housecanary.com/v2/property/value"
            query_params (dict): Dictionary of query params to add to the request.

        Returns:
            The result of calling this instance's OutputGenerator process_response method
            on the requests.Response object.
            If no OutputGenerator is specified for this instance, returns the requests.Response.
        """
        return self.execute_request(url, "GET", query_params, None)

    def post(self, url, post_data, query_params=None):
        """Makes a POST request to the specified url endpoint.

        Args:
            url (string): The url to the API without query params.
                          Example: "https://api.housecanary.com/v2/property/value"
            post_data: Json post data to send in the body of the request.
            query_params (dict): Optional. Dictionary of query params to add to the request.

        Returns:
            The result of calling this instance's OutputGenerator process_response method
            on the requests.Response object.
            If no OutputGenerator is specified for this instance, returns the requests.Response.
        """
        if query_params is None:
            query_params = {}

        return self.execute_request(url, "POST", query_params, post_data)
