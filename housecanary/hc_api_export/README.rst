HouseCanary Analytics API Export
=============================

HouseCanary Analytics API Export is a command line tool that allows you to call API endpoints
with a CSV file containing properties, blocks, zip codes and MSAs.

The input CSV file must contain a header row with columns indicating the identifiers.
Allowed identifiers are:

-  **address**
-  **zipcode**
-  **unit**
-  **city**
-  **state**
-  **slug**
-  **block_id**
-  **msa**
-  **client_value**
-  **client_value_sqft**
-  **num_bins**
-  **property_type**
-  **meta**

Other columns can be included but will be ignored.
See some example inputs `here <../../sample_input/>`_.

It generates an export of the Analytics API data in Excel or CSV format.

If exporting to Excel, this creates a single Excel file with a worksheet per endpoint.

If exporting to CSV, this creates a single CSV file per endpoint.

Installation
------------

``hc_api_export`` is installed as part of the HouseCanary client. If you haven't installed that yet, you can do so with ``pip``:

::

    pip install housecanary

Usage instructions
------------------

**Usage:**

::

    hc_api_export (<input> <endpoints>) [-t TYPE] [-o FILE] [-p PATH] [-k KEY] [-s SECRET] [-h?] [-r]

**Examples:**

::

    hc_api_export sample-input.csv property/* -t excel -o output.xlsx

    hc_api_export sample-input.csv property/value,property/school -t csv -p /home/my_output

    hc_api_export sample-input-blocks.csv block/* -t excel -o block_output.xlsx

    hc_api_export sample-input-zipcodes.csv zip/* -t excel -o zip_output.xlsx

    hc_api_export sample-input-msas.csv msa/* -t excel -o msa_output.xlsx

**Options:**

- input

    Required. An input CSV file containing property, zipcode, block or MSA identifiers

- endpoints

    Required. A comma separated list of endpoints to call like: ``property/value,property/school``

    To call all property endpoints, use ``property/\*``. The same applies for `block`, `zipcode` and `msa` endpoints.

    Only one level of endpoints can be called at a time, meaning you can't mix `property` and `block` endpoints.

- -t TYPE --type=TYPE

    Optional. An output type of ``excel`` or ``csv``. Default is ``excel``

- -o FILE --output=FILE

    Optional. A file name to output Excel results to. Only used when -t is ``excel``. Defaults to ``housecanary_output.xlsx``

- -p PATH --path=PATH

    Optional. A path to output CSV files to. Only used when -t is ``csv``. Defaults to ``housecanary_csv``

- -k KEY --key=KEY

    Optional API Key. Alternatively, you can use the HC_API_KEY environment variable

- -s SECRET --secret=SECRET

    Optional API Secret. Alternatively, you can use the HC_API_SECRET environment variable

- -r --retry

    Optional. When specified, if the API call fails due to exceeding the rate limit, the command will wait and retry once the limit has reset. However, if the rate limit will take more than 5 minutes to reset, the retry flag is ignored and the command will exit.

- -h -? --help

    Show usage instructions