"""Module for creating Excel exports of HouseCanary API data"""

import os
import csv
import time
from io import BytesIO
import openpyxl
from . import analytics_data_excel
from . import utilities
from .. import ApiClient
from .. import exceptions


def export_analytics_data_to_excel(data, output_file_name):
    """Creates an Excel file containing data returned by the Analytics API

    Args:
        data: Analytics API data as a list of dicts
        output_file_name: File name for output Excel file (use .xlsx extension).

    """
    workbook = create_excel_workbook(data)
    workbook.save(output_file_name)
    print 'Saved Excel file to {}'.format(output_file_name)


def export_analytics_data_to_csv(data, output_folder):
    """Creates CSV files containing data returned by the Analytics API.
       Creates one file per requested endpoint and saves it into the
       specified output_folder

    Args:
        data: Analytics API data as a list of dicts
        output_folder: Path to a folder to save the CSV files into
    """
    workbook = create_excel_workbook(data)

    suffix = '.csv'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for worksheet in workbook.worksheets:
        file_name = utilities.convert_title_to_snake_case(worksheet.title)

        file_path = os.path.join(output_folder, file_name + suffix)

        with open(file_path, 'wb') as output_file:
            csv_writer = csv.writer(output_file)
            for row in worksheet.rows:
                csv_writer.writerow([cell.value for cell in row])

    print 'Saved CSV files to {}'.format(output_folder)


def concat_excel_reports(addresses, output_file_name, endpoint, report_type,
                         retry, api_key, api_secret):
    """Creates an Excel file made up of combining the Value Report or Rental Report Excel
       output for the provided addresses.

    Args:
        addresses: A list of (address, zipcode) tuples
        output_file_name: A file name for the Excel output
        endpoint: One of 'value_report' or 'rental_report'
        report_type: One of 'full' or 'summary'
        retry: optional boolean to retry if rate limit is reached
        api_key: optional API Key
        api_secret: optional API Secret
    """
    # create the master workbook to output
    master_workbook = openpyxl.Workbook()

    if api_key is not None and api_secret is not None:
        client = ApiClient(api_key, api_secret)
    else:
        client = ApiClient()

    errors = []

    # for each address, call the API and load the xlsx content in a workbook.
    for index, addr in enumerate(addresses):
        print 'Processing {}'.format(addr[0])
        result = _get_excel_report(
            client, endpoint, addr[0], addr[1], report_type, retry, api_key, api_secret)

        if not result['success']:
            print 'Error retrieving report for {}'.format(addr[0])
            print result['content']
            errors.append({'address': addr[0], 'message': result['content']})
            continue

        orig_wb = openpyxl.load_workbook(filename=BytesIO(result['content']))

        # for each worksheet for this address
        for sheet_name in orig_wb.get_sheet_names():
            # if worksheet doesn't exist in master workbook, create it
            if sheet_name in master_workbook.get_sheet_names():
                master_ws = master_workbook.get_sheet_by_name(sheet_name)
            else:
                master_ws = master_workbook.create_sheet(sheet_name)

            # in the master work sheet,
            # write this address in the first column of the first available row
            # worksheet rows are 1-based.
            # if this isn't the first address, add an extra row for padding.
            next_row = 1 if index == 0 else master_ws.max_row + 2
            master_ws.cell(row=next_row, column=1, value=addr[0])

            orig_rows = orig_wb.get_sheet_by_name(sheet_name).rows

            # copy over the rest of the sheet's cells
            # starting at the row we left off at and one column over
            for orig_row_idx, orig_row in enumerate(orig_rows):
                for orig_cell_idx, orig_cell in enumerate(orig_row):
                    master_ws.cell(
                        row=next_row + orig_row_idx,
                        column=orig_cell_idx + 2,
                        value=orig_cell.value
                    )

    # remove the first sheet which will be empty
    master_workbook.remove(master_workbook.worksheets[0])

    # if any errors occurred, write them to an "Errors" worksheet
    if len(errors) > 0:
        errors_sheet = master_workbook.create_sheet('Errors')
        for error_idx, error in enumerate(errors):
            errors_sheet.cell(row=error_idx+1, column=1, value=error['address'])
            errors_sheet.cell(row=error_idx+1, column=2, value=error['message'])

    # save the master workbook to output_file_name
    master_workbook.save(output_file_name)
    print 'Saved output to {}'.format(os.path.join(os.getcwd(), output_file_name))


def _get_excel_report(client, endpoint, address, zipcode, report_type, retry, api_key, api_secret):
    if retry:
        while True:
            try:
                return _make_report_request(client, endpoint, address, zipcode, report_type)
            except exceptions.RateLimitException as e:
                rate_limit = e.rate_limits[0]
                utilities.print_rate_limit_error(rate_limit)

                if rate_limit['reset_in_seconds'] >= 300:
                    # Rate limit will take more than 5 minutes to reset, so just fail
                    return {'success': False, 'content': str(e)}

                print 'Will retry once rate limit resets...'
                time.sleep(rate_limit['reset_in_seconds'])
            except exceptions.RequestException as e:
                return {'success': False, 'content': str(e)}

    # otherwise just try once.
    try:
        return _make_report_request(client, endpoint, address, zipcode, report_type)
    except exceptions.RequestException as e:
        return {'success': False, 'content': str(e)}


def _make_report_request(client, endpoint, address, zipcode, report_type):
    if endpoint == 'rental_report':
        response = client.property.rental_report(address, zipcode, 'xlsx')
    else:
        response = client.property.value_report(address, zipcode, report_type, 'xlsx')
    return {'success': True, 'content': response.content}


def create_excel_workbook(data):
    """Calls the analytics_data_excel module to create the Workbook"""
    workbook = analytics_data_excel.get_excel_workbook(data)
    adjust_column_width_workbook(workbook)
    return workbook


def adjust_column_width_workbook(workbook):
    """Adjust column width for all sheets in workbook."""
    for worksheet in workbook.worksheets:
        adjust_column_width(worksheet)


def adjust_column_width(worksheet):
    """Adjust column width in worksheet.

    Args:
        worksheet: worksheet to be adjusted
    """
    dims = {}
    padding = 1
    for row in worksheet.rows:
        for cell in row:
            if not cell.value:
                continue
            dims[cell.column] = max(
                dims.get(cell.column, 0),
                len(str(cell.value))
            )
    for col, value in dims.items():
        worksheet.column_dimensions[col].width = value + padding
