HouseCanary API Python Client
=============================

The `HouseCanary <http://www.housecanary.com>`_ API Python Client provides an easy interface to call the HouseCanary API.


API documentation
-----------------

Full documentation is available at https://api-docs.housecanary.com

Installation
------------

To install:

::

    pip install housecanary

Basic Usage
-----------

.. code:: python

    import housecanary
    client = housecanary.ApiClient("my_api_key", "my_api_secret")
    result = client.property.value(("10216 N Willow Ave", "64157"))

    # result is an instance of housecanary.response.Response
    print result.json()

Authentication
--------------

When you create an instance of an ApiClient, you need to give it your
API key and secret. You can manage these in your settings page at
https://valuereport.housecanary.com/#/settings/api-settings.

You can pass these values to the ApiClient constructor:

.. code:: python

    client = housecanary.ApiClient("my_api_key", "my_api_secret")

Alternatively, instead of passing in your key and secret to the
constructor, you can store them in the following environment variables:

-  HC\_API\_KEY
-  HC\_API\_SECRET

Creating an instance of ApiClient with no arguments will read your key
and secret from those environment variables:

.. code:: python

    client = housecanary.ApiClient()

Usage Details
-------------

Endpoint methods
~~~~~~~~~~~~~~~~

The ApiClient class provides a ``property`` wrapper which contains
various methods for calling the endpoints of the Value Report, Rental Report and Analytics APIs:

Analytics API Endpoints:
^^^^^^^^^^^^^^^^^^^^^^^^^

-  **census**
-  **details**
-  **flood**
-  **mortgage_lien**
-  **msa_details**
-  **nod**
-  **owner_occupied**
-  **rental_value**
-  **sales_history**
-  **school**
-  **value**
-  **value_forecase**
-  **zip_details**
-  **zip_hpi_forecast**
-  **zip_hpi_historical**
-  **zip_volatility**
-  **component_mget**

Value Report API Endpoint:
^^^^^^^^^^^^^^^^^^^^^^^^^^

- **value_report**

Rental Report API Endpoint:
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **rental_report**

More wrapper objects may be added to ApiClient later like "zipcode" and
"lat\_lng".

**Args:**
     

All of the Analytics API endpoint methods take an
``address_data`` argument. ``address_data`` can be in one of two forms:

A Json formatted list like:

.. code:: python

    [{"address":"82 County Line Rd", "zipcode":"72173", "meta":"extra info"}]

Or, a list of (address, zipcode, meta) tuples like:

.. code:: python

    [("82 County Line Rd", "72173", "extra info")]

The "meta" field is optional. If you're only providing one address, you
can provide a tuple on it's own:

.. code:: python

    ("82 County Line Rd", "72173")

All of the endpoint methods of this class return a Response object or
the output of a custom OutputGenerator if one was specified in the
constructor.

**Example:**
        

.. code:: python

    client = housecanary.ApiClient()
    result = client.property.value([("10216 N Willow Ave", "64157"), ("82 County Line Rd", "72173")])

**Value Report:**
             

The ``value_report`` method behaves differently than the other endpoint
methods. It only supports one address at a time, and it takes some
extra, optional parameters:

Args: 
    - *address* (str) 
    - *zipcode* (str)

Kwargs: 
    - *report\_type* - "full" or "summary". Optional. Default is "full"
    - *format\_type* - "json", "pdf", "xlsx" or "all". Optional. Default is "json"

**Example:**
        

.. code:: python

    client = housecanary.ApiClient()
    # get Value Report in JSON format with "summary" report_type.
    result = client.property.value_report("10216 N Willow Ave", "64157", "summary", "json")
    # print the JSON output
    print result.json()

    # get Value Report in PDF format with "full" report_type.
    result = client.property.value_report("10216 N Willow Ave", "64157", format_type="pdf")
    # result is binary data of the PDF.

**Rental Report**

The ``rental_report`` method is for calling the Rental Report API. It only supports one address at a time.

Args:
    - *address* (str)
    - *zipcode* (str)

Kwargs: 
    - *format\_type* - "json", "xlsx" or "all". Optional. Default is "json"

Learn more about the various endpoints in the `API docs. <https://api-docs.housecanary.com/#endpoints>`_


Component_mget endpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may want to retrieve data from multiple Analytics API endpoints in one request. In this case, you can use the ``component_mget`` method. The ``component_mget`` method takes an ``address_data`` argument just like the other endpoint methods. Pass in a list of Analytics API endpoint names as the second argument. Note that ``value_report`` cannot be included.

**Example:**
        

.. code:: python

    client = housecanary.ApiClient()
    result = client.property.component_mget(("10216 N Willow Ave", "64157"), ["property/school", "property/census", "property/details"])


Response
~~~~~~~~

Response is a base class for encapsulating an HTTP response from the
HouseCanary API.

**Properties:**
           

-  **endpoint\_name** - Gets the endpoint name of the original request
-  **response** - Gets the underlying response object.

**Methods:**


-  **json()** - Gets the body of the response from the API as json.
-  **has\_object\_error()** - Returns true if any requested objects had
   a business logic error, otherwise returns false.
-  **get\_object\_errors()** - Gets a list of business error message
   strings for each of the requested objects that had a business error.
   If there was no error, returns an empty list.
-  **objects()** - Overridden in subclasses.
-  **rate_limits** - Returns a list of rate limit information

PropertyResponse
~~~~~~~~~~~~~~~~

A subclass of Response, this is returned for all property endpoints
except for ``value_report``.

**Methods:**
        

-  **objects()** - Gets a list of Property objects for the requested
   properties, each containing the object's returned json data from the
   API.
-  **properties()** - An alias for the objects() method.

HouseCanaryObject
~~~~~~~~~~~~~~~~~

Base class for various types of objects returned from the HouseCanary
API. Currently, only the Property subclass is implemented.

**Properties:**
           

-  **component\_results** - a list of ComponentResult objects that
   contain data and error information for each endpoint requested for
   this HouseCanaryObject.

**Methods:**
        

-  **has\_error()** - Returns a boolean of whether there was a business
   logic error fetching data for any components for this object.
-  **get\_errors()** - If there was a business error fetching data for
   any components for this object, returns the error messages.

Property
~~~~~~~~

A subclass of HouseCanaryObject, the Property represents a single
address and it's returned data.

**Properties:**
           

-  **address**
-  **zipcode**
-  **zipcode\_plus4**
-  **address\_full**
-  **city**
-  **country\_fips**
-  **lat**
-  **lng**
-  **state**
-  **unit**
-  **meta**

**Example:**
        

.. code:: python

    result = client.property.value(("123 Main St", "01234", "meta information"))
    p = result.properties()[0]
    print p.address
    # "123 Main St"
    print p.zipcode
    # "01234"
    print p.meta
    # "meta information"
    value_result = p.component_results[0]
    print value_result.component_name
    # 'property/value'
    print value_result.api_code
    # 0
    print value_result.api_code_description
    # 'ok'
    print value_result.json_data
    # {u'value': {u'price_upr': 1575138.0, u'price_lwr': 1326125.0, u'price_mean': 1450632.0, u'fsd': 0.086}}
    print p.has_error()
    # False
    print p.get_errors()
    # []

ValueReportResponse
~~~~~~~~~~~~~~~~~~~

A subclass of Response, this is the object returned for the
``value_report`` endpoint when "json" format\_type is used. It simply
returns the JSON data of the Value Report.

**Example:**
        

.. code:: python

    result = client.property.value_report("123 Main St", "01234")
    print result.json()

Command Line Tools
---------------------------
When you install this package, a couple command line tools are included and installed on your PATH.

- `HouseCanary Analytics API Export <housecanary/hc_api_export>`_
- `HouseCanary API Excel Concat <housecanary/hc_api_excel_concat>`_

License
-------

This API Client Library is made available under the MIT License:

The MIT License (MIT)

Copyright (c) 2016 HouseCanary, Inc

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For the avoidance of doubt, the above license does not apply to
HouseCanary's proprietary software code or APIs, or to any data,
analytics or reports made available by HouseCanary from time to time,
all of which may be licensed pursuant to a separate written agreement
