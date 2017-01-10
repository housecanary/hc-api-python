"""Utility functions for the housecanary.excel package"""

import json
import csv

ADDRESS_T = '{street_address} {city} {state} {zipcode}'


def get_formatted_address(data_dict):
    """Gets user friendly address string.

    Args:
        data_dict: Analytics API data as a dict
    """
    address = ''
    if 'address_info' in data_dict:
        address_info = data_dict['address_info']

        if 'address_full' in address_info:
            return address_info['address_full']

        address = ADDRESS_T.format(
            street_address=address_info.get('address', ''),
            city=address_info.get('city', ''),
            state=address_info.get('state', ''),
            zipcode=address_info.get('zipcode', '')
        )
    return address


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
    """Read addresses from input file into list of tuples."""
    with open(input_file_name, 'rb') as input_file:
        reader = csv.reader(input_file, delimiter=',', quotechar='"')
        addresses = map(tuple, reader)
        return addresses


def print_no_addresses():
    print 'No addresses were found in the input file'


def print_rate_limit_error(rate_limit):
    print "You have hit the API rate limit"
    print "Rate limit period: ", rate_limit["period"]
    print "Request limit: ", rate_limit["request_limit"]
    print "Requests remaining: ", rate_limit["requests_remaining"]
    print "Rate limit resets at: ", rate_limit["reset"]
    print "Time until rate limit resets: ", rate_limit["time_to_reset"]
