HouseCanary API Python Client
=============================

.. image:: https://img.shields.io/pypi/pyversions/housecanary.svg
    :target: https://pypi.python.org/pypi/housecanary

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

The ApiClient class provides a few wrappers which contain
various methods for calling the different API endpoints.

The property wrapper is used for calling the Analytics API Property endpoints as well
as the Value Report and Rental Report endpoints.

The block wrapper is used for calling the Analytics API Block endpoints.

The zip wrapper is used for calling the Analytics API Zip endpoints.

The msa wrapper is used for calling the Analytics API MSA endpoints.


Property Endpoints
~~~~~~~~~~~~~~~~~~

Analytics API Property Endpoints:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  **block_histogram_baths**
-  **block_histogram_beds**
-  **block_histogram_building_area**
-  **block_histogram_value**
-  **block_histogram_value_sqft**
-  **block_rental_value_distribution**
-  **block_value_distribution**
-  **block_value_ts**
-  **block_value_ts_historical**
-  **block_value_ts_forecast**
-  **census**
-  **details**
-  **flood**
-  **ltv**
-  **ltv_details**
-  **mortgage_lien**
-  **msa_details**
-  **msa_hpi_ts**
-  **msa_hpi_ts_forecast**
-  **msa_hpi_ts_historical**
-  **nod**
-  **owner_occupied**
-  **rental_value**
-  **rental_value_within_block**
-  **sales_history**
-  **school**
-  **value**
-  **value_forecast**
-  **value_within_block**
-  **zip_details**
-  **zip_hpi_forecast**
-  **zip_hpi_historical**
-  **zip_hpi_ts**
-  **zip_hpi_ts_forecast**
-  **zip_hpi_ts_historical**
-  **zip_volatility**
-  **component_mget**

Value Report API Endpoint:
^^^^^^^^^^^^^^^^^^^^^^^^^^

- **value_report**

Rental Report API Endpoint:
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **rental_report**


Args:
^^^^^     

All of the Analytics API property endpoint methods take an
``data`` argument. ``data`` can be in the following forms:

A dict like:

.. code:: python

    {"address": "82 County Line Rd", "zipcode": "72173", "meta": "someID"}

Or

.. code:: python

    {"address": "82 County Line Rd", "city": "San Francisco", "state": "CA", "meta": "someID"}

Or

.. code:: python

    {"slug": "123-Example-St-San-Francisco-CA-94105"}

A list of dicts as specified above:

.. code:: python

    [{"address": "82 County Line Rd", "zipcode": "72173", "meta": "someID"},
     {"address": "43 Valmonte Plaza", "zipcode": "90274", "meta": "someID2"}]

A single string representing a slug:

.. code:: python
    
    "123-Example-St-San-Francisco-CA-94105"

A tuple in the form of (address, zipcode, meta) like:

.. code:: python

    ("82 County Line Rd", "72173", "someID")

A list of (address, zipcode, meta) tuples like:

.. code:: python

    [("82 County Line Rd", "72173", "someID"),
     ("43 Valmonte Plaza", "90274", "someID2")]

Using a tuple only supports address, zipcode and meta. To specify city, state, unit or slug,
please use a dict.

The "meta" field is always optional.

The available keys in the dict are:
    - address (required if no slug)
    - slug (required if no address)
    - zipcode (optional)
    - unit (optional)
    - city (optional)
    - state (optional)
    - meta (optional)
    - client_value (optional, for ``value_within_block`` and ``rental_value_within_block``)
    - client_value_sqft (optional, for ``value_within_block`` and ``rental_value_within_block``)

All of the property endpoint methods return a PropertyResponse object
(or ValueReportResponse or RentalReportResponse) or
the output of a custom OutputGenerator if one was specified in the constructor.

**Examples:**
        

.. code:: python

    client = housecanary.ApiClient()
    result = client.property.value([("10216 N Willow Ave", "64157"), ("82 County Line Rd", "72173")])

    result = client.property.value({"address": "10216 N Willow Ave", "city": "San Francisco", "state": "CA"})

    result = client.property.value("123-Example-St-San-Francisco-CA-94105")


Component_mget endpoint
^^^^^^^^^^^^^^^^^^^^^^^

You may want to retrieve data from multiple Analytics API endpoints in one request.
In this case, you can use the ``component_mget`` method.
The ``component_mget`` method takes an ``address_data`` argument just like the other endpoint methods.
Pass in a list of Analytics API property endpoint names as the second argument.
Note that ``value_report`` and ``rental_report`` cannot be included.

**Example:**
        

.. code:: python

    client = housecanary.ApiClient()
    result = client.property.component_mget(("10216 N Willow Ave", "64157"), ["property/school", "property/census", "property/details"])


Value Report:
^^^^^^^^^^^^^

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

Rental Report:
^^^^^^^^^^^^^^

The ``rental_report`` method is for calling the Rental Report API. It only supports one address at a time.

Args:
    - *address* (str)
    - *zipcode* (str)

Kwargs: 
    - *format\_type* - "json", "xlsx" or "all". Optional. Default is "json"

Learn more about the various endpoints in the `API docs. <https://api-docs.housecanary.com/#endpoints>`_


Block Endpoints
~~~~~~~~~~~~~~~

Analytics API Block Endpoints:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  **histogram_baths**
-  **histogram_beds**
-  **histogram_building_area**
-  **histogram_value**
-  **histogram_value_sqft**
-  **rental_value_distribution**
-  **value_distribution**
-  **value_ts**
-  **value_ts_forecast**
-  **value_ts_historical**
-  **component_mget**

Args:
^^^^^

All of the Analytics API block endpoints take a ``block_data`` argument.
``block_data`` can be in the following forms:

A dict with a ``block_id`` like:

.. code:: python

    {"block_id": "060750615003005", "meta": "someId"}

For histogram endpoints you can include the ``num_bins`` key:

.. code:: python

    {"block_id": "060750615003005", "num_bins": 5, "meta": "someId"}

For time series and distribution endpoints you can include the ``property_type`` key:

.. code:: python

    {"block_id": "060750615003005", "property_type": "SFD", "meta": "someId"}

A list of dicts as specified above:

.. code:: python

    [{"block_id": "012345678901234", "meta": "someId"}, {"block_id": "012345678901234", "meta": "someId2}]

A single string representing a ``block_id``:

.. code:: python

    "012345678901234"

A list of ``block_id`` strings:

.. code:: python

    ["012345678901234", "060750615003005"]

The "meta" field is always optional.

See https://api-docs.housecanary.com/#analytics-api-block-level for more details
on the available parameters such as ``num_bins`` and ``property_type``.

All of the block endpoint methods return a BlockResponse,
or the output of a custom OutputGenerator if one was specified in the constructor.


**Examples:**
        
.. code:: python

    client = housecanary.ApiClient()
    result = client.block.histogram_baths("060750615003005")

    result = client.block.histogram_baths({"block_id": "060750615003005", "num_bins": 5})

    result = client.block.value_ts({"block_id": "060750615003005", "property_type": "SFD"})

    result = client.block.value_ts([{"block_id": "060750615003005", "property_type": "SFD"}, {"block_id": "012345678901234", "property_type": "SFD"}])

    result = client.block.value_distribution(["012345678901234", "060750615003005"])


Zip Endpoints
~~~~~~~~~~~~~~~

Analytics API Zip Endpoints:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  **details**
-  **hpi_forecast**
-  **hpi_historical**
-  **hpi_ts**
-  **hpi_ts_forecast**
-  **hpi_ts_historical**
-  **volatility**
-  **component_mget**

Args:
^^^^^

All of the Analytics API zip endpoints take a ``zip_data`` argument.
``zip_data`` can be in the following forms:

A dict with a ``zipcode`` like:

.. code:: python

    {"zipcode": "90274", "meta": "someId"}

A list of dicts as specified above:

.. code:: python

    [{"zipcode": "90274", "meta": "someId"}, {"zipcode": "01960", "meta": "someId2}]

A single string representing a ``zipcode``:

.. code:: python

    "90274"

A list of ``zipcode`` strings:

.. code:: python

    ["90274", "01960"]

The "meta" field is always optional.

All of the zip endpoint methods return a ZipCodeResponse,
or the output of a custom OutputGenerator if one was specified in the constructor.


**Examples:**
        
.. code:: python

    client = housecanary.ApiClient()
    result = client.zip.details("90274")

    result = client.zip.details({"zipcode": "90274", "meta": "someId"})

    result = client.zip.details([{"zipcode": "90274", "meta": "someId"}, {"zipcode": "01960", "meta": "someId2"}])

    result = client.zip.details(["90274", "01960"])


MSA Endpoints
~~~~~~~~~~~~~~~

Analytics API MSA Endpoints:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  **details**
-  **hpi_ts**
-  **hpi_ts_forecast**
-  **hpi_ts_historical**
-  **component_mget**

Args:
^^^^^

All of the Analytics API MSA endpoints take an ``msa_data`` argument.
``msa_data`` can be in the following forms:

A dict with an ``msa`` like:

.. code:: python

    {"msa": "41860", "meta": "someId"}

A list of dicts as specified above:

.. code:: python

    [{"msa": "41860", "meta": "someId"}, {"msa": "40928", "meta": "someId2}]

A single string representing a ``msa``:

.. code:: python

    "41860"

A list of ``msa`` strings:

.. code:: python

    ["41860", "40928"]

The "meta" field is always optional.

All of the msa endpoint methods return an MsaResponse,
or the output of a custom OutputGenerator if one was specified in the constructor.


**Examples:**
        
.. code:: python

    client = housecanary.ApiClient()
    result = client.msa.details("41860")

    result = client.msa.details({"msa": "90274", "meta": "someId"})

    result = client.msa.details([{"msa": "41860", "meta": "someId"}, {"msa": "40928", "meta": "someId2"}])

    result = client.msa.details(["41860", "40928"])


Response Objects
~~~~~~~~~~~~~~~~

Response
^^^^^^^^

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
^^^^^^^^^^^^^^^^

A subclass of Response, this is returned for all property endpoints
except for ``value_report`` and ``rental_report``.

**Methods:**
        

-  **objects()** - Gets a list of Property objects for the requested
   properties, each containing the object's returned json data from the
   API.
-  **properties()** - An alias for the objects() method.

BlockResponse
^^^^^^^^^^^^^^^^

A subclass of Response, this is returned for all block endpoints.

**Methods:**
        

-  **objects()** - Gets a list of Block objects for the requested
   blocks, each containing the object's returned json data from the
   API.
-  **blocks()** - An alias for the objects() method.

ZipCodeResponse
^^^^^^^^^^^^^^^^

A subclass of Response, this is returned for all zip endpoints.

**Methods:**
        

-  **objects()** - Gets a list of ZipCode objects for the requested
   zipcodes, each containing the object's returned json data from the
   API.
-  **zipcodes()** - An alias for the objects() method.

MsaResponse
^^^^^^^^^^^^^^^^

A subclass of Response, this is returned for all msa endpoints.

**Methods:**
        

-  **objects()** - Gets a list of Msa objects for the requested
   msas, each containing the object's returned json data from the
   API.
-  **msas()** - An alias for the objects() method.

HouseCanaryObject
^^^^^^^^^^^^^^^^^

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
^^^^^^^^

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


Block
^^^^^

A subclass of HouseCanaryObject, the Block represents a single
block and it's returned data.

**Properties:**
           

-  **block_id**
-  **property_type**
-  **meta**

**Example:**
        

.. code:: python

    result = client.block.value_ts("060750615003005")
    b = result.blocks()[0]
    print b.block_id
    # "060750615003005"
    print b.meta
    # "meta information"
    value_result = b.component_results[0]
    print value_result.component_name
    # 'block/value_ts'
    print value_result.api_code
    # 0
    print value_result.api_code_description
    # 'ok'
    print value_result.json_data
    # [...data...]
    print b.has_error()
    # False
    print b.get_errors()
    # []


ZipCode
^^^^^^^

A subclass of HouseCanaryObject, the ZipCode represents a single
zipcode and it's returned data.

**Properties:**
           

-  **zipcode**
-  **meta**

**Example:**
        

.. code:: python

    result = client.zip.details("90274")
    z = result.zipcodes()[0]
    print z.zipcode
    # "90274"
    print z.meta
    # "meta information"
    details_result = z.component_results[0]
    print details_result.component_name
    # 'zip/details'
    print details_result.api_code
    # 0
    print details_result.api_code_description
    # 'ok'
    print details_result.json_data
    # [...data...]
    print z.has_error()
    # False
    print z.get_errors()
    # []


Msa
^^^^^^^

A subclass of HouseCanaryObject, the Msa represents a single
Metropolitan Statistical Area and it's returned data.

**Properties:**
           

-  **msa**
-  **meta**

**Example:**
        

.. code:: python

    result = client.msa.details("41860")
    m = result.msas()[0]
    print m.msa
    # "41860"
    print m.meta
    # "meta information"
    details_result = m.component_results[0]
    print details_result.component_name
    # 'msa/details'
    print details_result.api_code
    # 0
    print details_result.api_code_description
    # 'ok'
    print details_result.json_data
    # [...data...]
    print m.has_error()
    # False
    print m.get_errors()
    # []


ValueReportResponse
^^^^^^^^^^^^^^^^^^^

A subclass of Response, this is the object returned for the
``value_report`` endpoint when "json" format\_type is used. It simply
returns the JSON data of the Value Report.

**Example:**
        

.. code:: python

    result = client.property.value_report("123 Main St", "01234")
    print result.json()

RentalReportResponse
^^^^^^^^^^^^^^^^^^^^

A subclass of Response, this is the object returned for the
``rental_report`` endpoint when "json" format\_type is used. It simply
returns the JSON data of the Rental Report.

**Example:**
        

.. code:: python

    result = client.property.rental_report("123 Main St", "01234")
    print result.json()

Command Line Tools
---------------------------
When you install this package, a couple command line tools are included and installed on your PATH.

- `HouseCanary Analytics API Export <housecanary/hc_api_export>`_
- `HouseCanary API Excel Concat <housecanary/hc_api_excel_concat>`_

Running Tests
---------------------------

To run the unit test suite:

::

    python setup.py nosetests --with-coverage --cover-package=housecanary

During unit tests, all API requests are mocked.
You can run the unit tests with real API requests by doing the following:


- Update `URL_PREFIX` in `constants.py` to point to a test or dev environment
- Obtain an account for that environment that has permissions to all API components
- Obtain an API Key and Secret and put them in `HC_API_KEY` and `HC_API_SECRET` environment variables
- Run the test suite as: 

::

    HC_API_CALLS=true python setup.py nosetests

**Note:** This setting will be ignored and API requests will be mocked if `URL_PREFIX` is pointing to Production.

License
-------

This API Client Library is made available under the MIT License:

The MIT License (MIT)

Copyright (c) 2017 HouseCanary, Inc

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
