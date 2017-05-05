HouseCanary API Excel Concat
=============================

HouseCanary API Excel Concat is a command line tool that allows you to call the
Value Report or Rental Report API for multiple addresses by passing in a CSV file
containing addresses and zip codes.

The input CSV file must contain a header row with columns for ``address`` and ``zipcode``.
Other columns can be included as identifiers.
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

    hc_api_excel_concat (<input>) [-o FILE] [-f PATH] [-e ENDPOINT] [-k KEY] [-s SECRET] [-t TYPE] [-h?] [-r]

**Example:**
::

    hc_api_excel_concat sample-input.csv -o vr_output.xlsx -f vr_files -e value_report

    hc_api_excel_concat sample-input.csv -o rr_output.xlsx -f rr_files -e rental_report

**Options:**

- input

    Required. An input CSV file containing addresses and zipcodes

- -o FILE --output=FILE

    Optional. A file name for the combined Excel output. The file name you specify should have the ``.xlsx`` extension. Defaults to ``output.xlsx``

- -f PATH --files=PATH

    Optional. A path to save the individual Excel files for each address. Defaults to 'output_files'.

- -e ENDPOINT --endpoint=ENDPOINT

    Optional. One of 'value_report' or 'rental_report' to determine which API endpoint to call. Defaults to 'value_report'

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