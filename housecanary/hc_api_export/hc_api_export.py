"""hc_api_export - Takes a CSV file containing rows of addresses and zipcodes, calls
                the specified HouseCanary API endpoints to retrieve data
                for the addresses and outputs the data to Excel or CSV.

                If exporting to Excel, this creates a single Excel file
                with a worksheet per endpoint.

                If exporting to CSV, this creates a single CSV file per endpoint.

Usage: hc_api_export (<input> <endpoints>) [-t TYPE] [-o FILE] [-p PATH] [-k KEY] [-s SECRET] [-h?] [-r]

Examples:
    hc_api_export sample_input/sample-input.csv property/* -t excel -o output.xlsx

    hc_api_export sample_input/sample-input.csv property/value,property/school -t csv -p /home/my_output

Options:
    input                     Required. An input CSV file containing addresses and zipcodes

    endpoints                 Required. A comma separated list of endpoints to call like:
                              'property/value,property/school'
                              To call all endpoints, use 'property/*'

    -t TYPE --type=TYPE       Optional. An output type of 'excel' or 'csv'. Default is 'excel'

    -o FILE --output=FILE     Optional. A file name to output Excel results to.
                              Only used when -t is 'excel'.
                              Defaults to 'housecanary_output.xlsx'

    -p PATH --path=PATH       Optional. A path to output CSV files to.
                              Only used when -t is 'csv'.
                              Defaults to 'housecanary_csv'

    -k KEY --key=KEY          Optional API Key. Alternatively, you can use the HC_API_KEY
                              environment variable

    -s SECRET --secret=SECRET Optional API Secret. Alternatively, you can use the HC_API_SECRET
                              environment variable

    -r --retry                Optional. When specified, if the API call fails due to exceeding
                              the rate limit, the command will wait and retry once the limit
                              has reset. However, if the rate limit will take more than 5 minutes
                              to reset, the retry flag is ignored and the command will exit.

    -h -? --help              Show usage
"""


import sys
import time
from docopt import docopt
import housecanary


def hc_api_export(docopt_args):
    input_file_name = docopt_args['<input>']
    output_type = docopt_args['--type'] or 'excel'
    output_file_name = docopt_args['--output'] or 'housecanary_output.xlsx'
    output_csv_path = docopt_args['--path'] or 'housecanary_csv'
    endpoints = docopt_args['<endpoints>']
    api_key = docopt_args['--key'] or None
    api_secret = docopt_args['--secret'] or None
    retry = docopt_args['--retry'] or False

    addresses = housecanary.utilities.get_addresses_from_input_file(input_file_name)

    if len(addresses) == 0:
        housecanary.utilities.print_no_addresses()
        sys.exit(2)

    if endpoints == 'property/*':
        endpoints = ['property/census', 'property/details', 'property/flood',
                     'property/mortgage_lien', 'property/msa_details', 'property/nod',
                     'property/owner_occupied', 'property/rental_value', 'property/sales_history',
                     'property/school', 'property/value', 'property/value_forecast',
                     'property/zip_details', 'property/zip_hpi_forecast',
                     'property/zip_hpi_historical']
    else:
        endpoints = endpoints.split(",")

    if 'property/value_report' in endpoints:
        print(("property/value_report is not allowed for export to Excel. "
               "Please use the Value Report application to get Excel outputs of Value Reports."))
        return

    if retry:
        # If rate limit exceeded, enter retry process
        api_result = __get_results_from_api_with_retry(addresses, endpoints, api_key, api_secret)
    else:
        # Just try once and exit if rate limit exceeded
        try:
            api_result = _get_results_from_api(addresses, endpoints, api_key, api_secret)
        except housecanary.exceptions.RateLimitException as e:
            housecanary.utilities.print_rate_limit_error(e.rate_limits[0])
            sys.exit(2)

    all_data = api_result.json()

    if output_type.lower() == 'csv':
        housecanary.export_analytics_data_to_csv(all_data, output_csv_path)
    else:
        housecanary.export_analytics_data_to_excel(all_data, output_file_name)


def __get_results_from_api_with_retry(addresses, endpoints, api_key, api_secret):
    while True:
        try:
            return _get_results_from_api(addresses, endpoints, api_key, api_secret)
        except housecanary.exceptions.RateLimitException as e:
            rate_limit = e.rate_limits[0]
            housecanary.utilities.print_rate_limit_error(rate_limit)
            if rate_limit["reset_in_seconds"] < 300:
                print "Will retry once rate limit resets..."
                time.sleep(rate_limit["reset_in_seconds"])
            else:
                # Rate limit will take more than 5 minutes to reset, so just exit
                sys.exit(2)


def _get_results_from_api(addresses, endpoints, api_key, api_secret):
    """Use the HouseCanary API Python Client to access the API"""

    if api_key is not None and api_secret is not None:
        client = housecanary.ApiClient(api_key, api_secret)
    else:
        client = housecanary.ApiClient()

    if len(endpoints) > 1:
        # use component_mget to request multiple endpoints in one call
        return client.property.component_mget(addresses, endpoints)
    else:
        return client.property.fetch_property_component(endpoints[0], addresses)


def main():
    args = docopt(__doc__)
    hc_api_export(args)
