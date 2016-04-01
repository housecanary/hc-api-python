hc-api-python
--------

To use, simply do::

    >>> import hcapi
    >>> client = hcapi.HouseCanaryClient("my_auth_key", "my_secret")
    >>> res = client.get("value_report", "700 Boylston St", "02116")