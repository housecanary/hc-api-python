HouseCanary Analytics API Export
=============================

HouseCanary Analytics API Export is a command line tool that allows you to call API endpoints
with a CSV file containing addresses and zip codes.

The input CSV file must contain a header row with columns for ``address`` and ``zipcode``.
Other columns can be included but will be ignored.
See an example input `here <../../sample_input/sample-input.csv>`_.

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

**Options:**

- input

    Required. An input CSV file containing addresses and zipcodes

- endpoints

    Required. A comma separated list of endpoints to call like: ``property/value,property/school``

    To call all endpoints, use ``property/\*``

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