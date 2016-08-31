"""Module for creating exports of Analytics API data"""

import os
import csv
from . import analytics_data_excel
from . import utilities


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
