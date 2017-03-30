"""hc_api_export - Takes a CSV file containing rows of property, zipcode, block or MSA identifiers,
                   calls the specified HouseCanary API endpoints to retrieve data
                   for the identifiers and outputs the data to Excel or CSV.

                   The input CSV file must contain a header row with columns indicating the identifiers.
                   Allowed identifiers are:
                   - address
                   - zipcode
                   - unit
                   - city
                   - state
                   - slug
                   - block_id
                   - msa
                   - client_value
                   - client_value_sqft
                   - num_bins
                   - property_type
                   - meta

                   If exporting to Excel, this creates a single Excel file
                   with a worksheet per endpoint.

                   If exporting to CSV, this creates a single CSV file per endpoint.

Usage: hc_api_export (<input> <endpoints>) [-t TYPE] [-o FILE] [-p PATH] [-k KEY] [-s SECRET] [-h?] [-r]

Examples:
    hc_api_export sample_input/sample-input.csv property/* -t excel -o output.xlsx

    hc_api_export sample_input/sample-input.csv property/value,property/school -t csv -p /home/my_output

    hc_api_export sample_input/sample-input-blocks.csv block/* -t excel -o block_output.xlsx

    hc_api_export sample_input/sample-input-zipcodes.csv zip/* -t excel -o zip_output.xlsx

    hc_api_export sample_input/sample-input-msas.csv msa/* -t excel -o msa_output.xlsx

Options:
    input                     Required. An input CSV file containing addresses and zipcodes

    endpoints                 Required. A comma separated list of endpoints to call like:
                                'property/value,property/school'
                              To call all endpoints,
                                use 'property/*', 'block/*', 'zipcode/*' or 'msa/*'.
                              Only one level of endpoints can be called at a time,
                                meaning you can't mix 'property' and 'block' endpoints.

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


from __future__ import print_function
import sys
import time
from builtins import str
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

    try:
        identifiers = housecanary.excel_utilities.get_identifiers_from_input_file(input_file_name)
    except Exception as ex:
        print(str(ex))
        sys.exit(2)

    if len(identifiers) == 0:
        print('No identifiers were found in the input file')
        sys.exit(2)

    if ',' in endpoints:
        endpoints = endpoints.split(',')
    elif '*' in endpoints:
        endpoints = housecanary.excel_utilities.get_all_endpoints(endpoints.split('/')[0])
    else:
        endpoints = [endpoints]

    if 'property/value_report' in endpoints or 'property/rental_report' in endpoints:
        print(("property/value_report and property/rental_report"
               "are not allowed for export to Excel."
               "Please use the Value Report application to get Excel outputs of Value Reports."))
        return

    if retry:
        # If rate limit exceeded, enter retry process
        api_result = __get_results_from_api_with_retry(identifiers, endpoints, api_key, api_secret)
    else:
        # Just try once and exit if rate limit exceeded
        try:
            api_result = _get_results_from_api(identifiers, endpoints, api_key, api_secret)
        except housecanary.exceptions.RateLimitException as e:
            housecanary.excel_utilities.print_rate_limit_error(e.rate_limits[0])
            sys.exit(2)

    all_data = api_result.json()

    result_info_key = _get_result_info_key(endpoints[0].split('/')[0])
    identifier_keys = list(identifiers[0].keys())

    if output_type.lower() == 'csv':
        housecanary.export_analytics_data_to_csv(
            all_data, output_csv_path, result_info_key, identifier_keys)
    else:
        housecanary.export_analytics_data_to_excel(
            all_data, output_file_name, result_info_key, identifier_keys)


def __get_results_from_api_with_retry(identifiers, endpoints, api_key, api_secret):
    while True:
        try:
            return _get_results_from_api(identifiers, endpoints, api_key, api_secret)
        except housecanary.exceptions.RateLimitException as e:
            rate_limit = e.rate_limits[0]
            housecanary.excel_utilities.print_rate_limit_error(rate_limit)
            if rate_limit["reset_in_seconds"] < 300:
                print("Will retry once rate limit resets...")
                time.sleep(rate_limit["reset_in_seconds"])
            else:
                # Rate limit will take more than 5 minutes to reset, so just exit
                sys.exit(2)


def _get_results_from_api(identifiers, endpoints, api_key, api_secret):
    """Use the HouseCanary API Python Client to access the API"""

    if api_key is not None and api_secret is not None:
        client = housecanary.ApiClient(api_key, api_secret)
    else:
        client = housecanary.ApiClient()

    wrapper = getattr(client, endpoints[0].split('/')[0])

    if len(endpoints) > 1:
        # use component_mget to request multiple endpoints in one call
        return wrapper.component_mget(identifiers, endpoints)
    else:
        return wrapper.fetch_identifier_component(endpoints[0], identifiers)


def _get_result_info_key(level):
    if level == 'property':
        return 'address_info'
    if level == 'block':
        return 'block_info'
    if level == 'zip':
        return 'zipcode_info'
    if level == 'msa':
        return 'msa_info'
    raise Exception('Invalid endpoint level found: {}'.format(level))


def main():
    args = docopt(__doc__)
    hc_api_export(args)
