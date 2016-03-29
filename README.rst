hc-python-client
--------

To use, simply do::

    >>> import hcclient
    >>> client = hcclient.HouseCanaryClient("my_auth_key", "my_secret")
    >>> res = client.get("value_report", "700 Boylston St", "02116")