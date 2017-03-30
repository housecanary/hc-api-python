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
    """Read addresses from input file into list of tuples.
       This only supports address and zipcode headers
    """
    mode = 'r'
    if sys.version_info[0] < 3:
        mode = 'rb'
    with io.open(input_file_name, mode) as input_file:
        reader = csv.reader(input_file, delimiter=',', quotechar='"')

        addresses = list(map(tuple, reader))

        if len(addresses) == 0:
            raise Exception('No addresses found in input file')

        header_columns = list(column.lower() for column in addresses.pop(0))

        try:
            address_index = header_columns.index('address')
            zipcode_index = header_columns.index('zipcode')
        except ValueError:
            raise Exception("""The first row of the input CSV must be a header that contains \
a column labeled 'address' and a column labeled 'zipcode'.""")

        return list((row[address_index], row[zipcode_index]) for row in addresses)


def get_identifiers_from_input_file(input_file_name):
    """Read identifiers from input file into list of dicts with the header row values
       as keys, and the rest of the rows as values.
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
