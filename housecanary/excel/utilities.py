"""Utility functions for the housecanary.excel package"""

from __future__ import print_function
import json
import csv
import io
import sys
from builtins import map


def normalize_cell_value(value):
    """Process value for writing into a cell.

    Args:
        value: any type of variable

    Returns:
        json serialized value if value is list or dict, else value
    """
    if isinstance(value, dict) or isinstance(value, list):
        return json.dumps(value)
    return value


def convert_snake_to_title_case(key):
    """Converts snake-cased key to title-cased key."""
    return ' '.join(w.capitalize() for w in key.split('_'))


def convert_title_to_snake_case(key):
    """Converts title-cased key to snake-cased key."""
    return '_'.join(w.lower() for w in key.split(' '))


def get_addresses_from_input_file(input_file_name):
    """Read identifiers from input file into list of dicts with the header row values
       as keys, and the rest of the rows as values.
       This is used by hc_api_excel_concat.
    """
    mode = 'r'
    if sys.version_info[0] < 3:
        mode = 'rb'
    with io.open(input_file_name, mode) as input_file:
        result = [{identifier: val for identifier, val in list(row.items())}
                  for row in csv.DictReader(input_file, skipinitialspace=True)]

        if len(result) > 0:
            first_row = result[0]
            keys = [k.lower() for k in first_row.keys()]
            if 'address' not in keys or 'zipcode' not in keys:
                raise Exception("""The first row of the input CSV must be a header that contains \
a column labeled 'address' and a column labeled 'zipcode'.""")

        return result


def get_identifiers_from_input_file(input_file_name):
    """Read identifiers from input file into list of dicts with the header row values
       as keys, and the rest of the rows as values.
       This is used by hc_api_export.
    """
    valid_identifiers = ['address', 'zipcode', 'unit', 'city', 'state', 'slug', 'block_id', 'msa',
                         'num_bins', 'property_type', 'client_value', 'client_value_sqft', 'meta']
    mode = 'r'
    if sys.version_info[0] < 3:
        mode = 'rb'
    with io.open(input_file_name, mode) as input_file:
        result = [{identifier: val for identifier, val in list(row.items())
                   if identifier in valid_identifiers}
                  for row in csv.DictReader(input_file, skipinitialspace=True)]
        return result


def get_extra_identifiers_from_input_file(input_file_name):
    """Read extra identifiers from input file into list of dicts with the header row values
       as keys, and the rest of the rows as values.
       These extra identifiers are those that are not used for making the API requests.
       This is used by hc_api_export.
    """
    identifiers_to_skip = ['address', 'zipcode', 'unit', 'city', 'state', 'slug', 'block_id', 'msa',
                           'num_bins', 'property_type', 'client_value', 'client_value_sqft', 'meta']
    mode = 'r'
    if sys.version_info[0] < 3:
        mode = 'rb'
    with io.open(input_file_name, mode) as input_file:
        result = [{identifier: val for identifier, val in list(row.items())
                   if identifier not in identifiers_to_skip}
                  for row in csv.DictReader(input_file, skipinitialspace=True)]
        return result


def print_rate_limit_error(rate_limit):
    print("You have hit the API rate limit")
    print("Rate limit period: ", rate_limit["period"])
    print("Request limit: ", rate_limit["request_limit"])
    print("Requests remaining: ", rate_limit["requests_remaining"])
    print("Rate limit resets at: ", rate_limit["reset"])
    print("Time until rate limit resets: ", rate_limit["time_to_reset"])


def get_all_endpoints(level):
    if level == 'property':
        return ['property/block_histogram_baths',
                'property/block_histogram_beds',
                'property/block_histogram_building_area',
                'property/block_histogram_value',
                'property/block_histogram_value_sqft',
                'property/block_rental_value_distribution',
                'property/block_value_distribution',
                'property/block_value_ts',
                'property/block_value_ts_historical',
                'property/block_value_ts_forecast',
                'property/census',
                'property/details',
                'property/flood',
                'property/geocode',
                'property/ltv',
                'property/ltv_details',
                'property/mortgage_lien',
                'property/msa_details',
                'property/msa_hpi_ts',
                'property/msa_hpi_ts_forecast',
                'property/msa_hpi_ts_historical',
                'property/nod',
                'property/owner_occupied',
                'property/rental_value',
                'property/rental_value_within_block',
                'property/sales_history',
                'property/school',
                'property/value',
                'property/value_forecast',
                'property/value_within_block',
                'property/zip_details',
                'property/zip_hpi_forecast',
                'property/zip_hpi_historical',
                'property/zip_hpi_ts',
                'property/zip_hpi_ts_forecast',
                'property/zip_hpi_ts_historical',
                'property/zip_volatility']

    if level == 'block':
        return ['block/histogram_baths',
                'block/histogram_beds',
                'block/histogram_building_area',
                'block/histogram_value',
                'block/histogram_value_sqft',
                'block/rental_value_distribution',
                'block/value_distribution',
                'block/value_ts',
                'block/value_ts_forecast',
                'block/value_ts_historical']

    if level == 'zip':
        return ['zip/details',
                'zip/hpi_forecast',
                'zip/hpi_historical',
                'zip/hpi_ts',
                'zip/hpi_ts_forecast',
                'zip/hpi_ts_historical',
                'zip/volatility']

    if level == 'msa':
        return ['msa/details',
                'msa/hpi_ts',
                'msa/hpi_ts_forecast',
                'msa/hpi_ts_historical']

    raise Exception('Invalid endpoint level specified: {}'.format(level))
