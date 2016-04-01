hc-api-python
--------

# Installation
To install::

	>>> pip install hc-api-python

# Usage
Basic usage::

    >>> import hcapi
    >>> client = hcapi.HouseCanaryClient("my_auth_key", "my_secret")
    >>> res = client.get("value_report", "700 Boylston St", "02116", "json")