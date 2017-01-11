HouseCanary API Excel Concat
=============================

HouseCanary API Excel Concat is a command line tool that allows you to call the
Value Report or Rental Report API for multiple addresses by passing in a CSV file
containing addresses and zip codes.

Each row in the input CSV file should be in the format of ``address,zipcode``.
See an example input `here <../../sample_input/sample-input.csv>`_.

It generates a single .xlsx file which combines the Excel output of each address.

Installation
------------

``hc_api_excel_concat`` is installed as part of the HouseCanary client.
If you haven't installed that yet, you can do so with ``pip``:

::

    pip install housecanary


Usage instructions:
-------------------

**Usage:**
::

    hc_api_excel_concat (<input>) [-o FILE] [-e ENDPOINT] [-k KEY] [-s SECRET] [-t TYPE] [-H] [-h?] [-r]

**Example:**
::

    hc_api_excel_concat sample-input.csv -o vr_output.xlsx -e value_report -H

    hc_api_excel_concat sample-input.csv -o rr_output.xlsx -e rental_report -H

**Options:**

- input

    Required. An input CSV file containing addresses and zipcodes

- -o FILE --output=FILE

    Optional. A file name for the Excel output. The file name you specify should have the ``.xlsx`` extension. Defaults to ``output.xlsx``

- -e ENDPOINT --endpoint=ENDPOINT

    Optional. One of 'value_report' or 'rental_report' to determine which API endpoint to call. Defaults to 'value_report'

- -H --header

    Optional. Indicates that the input file has a header row that should be ignored

- -k KEY --key=KEY
    
    Optional API Key. Alternatively, you can use the HC_API_KEY environment variable

- -s SECRET --secret=SECRET

    Optional API Secret. Alternatively, you can use the HC_API_SECRET environment variable

- -t TYPE --type=TYPE

    Optional Report Type of ``full`` or ``summary``. Default is ``full``

- -r --retry

    Optional. When specified, if any of the API calls fail due to exceeding the rate limit, the command will wait and retry once the limit has reset. However, if the rate limit will take more than 5 minutes to reset, the retry flag is ignored and the command will exit.

- -h -? --help

    Show usage instructions