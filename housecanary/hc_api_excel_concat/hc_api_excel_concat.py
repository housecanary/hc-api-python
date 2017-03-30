"""hc_api_excel_concat - Takes a CSV file containing rows of addresses and zipcodes,
                calls the HouseCanary Value Report or Rental Report API to retrieve Excel output
                for the addresses and combines the results into a single Excel file.

Usage: hc_api_excel_concat (<input>) [-o FILE] [-f PATH] [-e ENDPOINT] [-k KEY] [-s SECRET] [-t TYPE] [-h?] [-r]

Examples:
    hc_api_excel_concat sample_input/sample-input.csv -o vr_output.xlsx -f output_files -e value_report

    hc_api_excel_concat sample_input/sample-input.csv -o rr_output.xlsx -f output_files -e rental_report

Options:
    input                     Required. An input CSV file containing addresses and zipcodes

    -o FILE --output=FILE     Optional. A file name for the Excel output.
                              Defaults to 'output.xlsx'

    -f PATH --files=PATH      Optional. A path to save the individual Excel files for each address.
                              Defaults to 'output_files'.

    -e ENDPOINT --endpoint=ENDPOINT Optional. One of 'value_report' or 'rental_report'
                                    to determine which API endpoint to call.
                                    Defaults to 'value_report'

    -k KEY --key=KEY          Optional API Key. Alternatively, you can use the HC_API_KEY
                              environment variable

    -s SECRET --secret=SECRET Optional API Secret. Alternatively, you can use the HC_API_SECRET
                              environment variable

    -t TYPE --type=TYPE       Optional Report Type of 'full' or 'summary'. Default is 'full'

    -r --retry                Optional. When specified, if any of the API calls fail due to
                              exceeding the rate limit, the command will wait and retry once
                              the limit has reset. However, if the rate limit will take more
                              than 5 minutes to reset, the retry flag is ignored and the
                              command will exit.

    -h -? --help              Show usage
"""


from __future__ import print_function
import sys
from builtins import str
from docopt import docopt
import housecanary


def hc_api_excel_concat(docopt_args):
    input_file_name = docopt_args['<input>']
    output_file_name = docopt_args['--output'] or 'output.xlsx'
    endpoint = docopt_args['--endpoint'] or 'value_report'
    api_key = docopt_args['--key'] or None
    api_secret = docopt_args['--secret'] or None
    report_type = docopt_args['--type'] or 'full'
    retry = docopt_args['--retry'] or False
    files_path = docopt_args['--files'] or 'output_files'

    try:
        addresses = housecanary.excel_utilities.get_addresses_from_input_file(input_file_name)
    except Exception as ex:
        print(str(ex))
        sys.exit(2)

    if len(addresses) == 0:
        print('No addresses were found in the input file')
        sys.exit(2)

    if endpoint != 'value_report' and endpoint != 'rental_report':
        print("""Invalid endpoint '{}'. Must be one of 'value_report' or 'rental_report'.
You can omit the endpoint param to default to 'value_report'""".format(endpoint))
        sys.exit(2)

    housecanary.concat_excel_reports(
        addresses, output_file_name, endpoint, report_type, retry, api_key, api_secret, files_path)


def main():
    args = docopt(__doc__)
    hc_api_excel_concat(args)
