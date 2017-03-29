import unittest
import os
import shutil
from housecanary.hc_api_export import hc_api_export


class HcApiExportTestCase(unittest.TestCase):
    """Tests for the hc_api_export tool"""

    def setUp(self):
        self.output_excel_file = 'unittest_hc_api_export.xlsx'
        self.output_csv_path = 'unittest_housecanary_csv'
        self._remove_test_output()

    def tearDown(self):
        self._remove_test_output()

    def _remove_test_output(self):
        if os.path.exists(self.output_excel_file):
            os.remove(self.output_excel_file)
        if os.path.exists(self.output_csv_path):
            shutil.rmtree(self.output_csv_path)

    def get_docopt_args(self, output_type, endpoints, input_file):
        return {
            '--help': False,
            '--key': None,
            '--output': self.output_excel_file,
            '--path': self.output_csv_path,
            '--retry': False,
            '--secret': None,
            '--type': output_type,
            '-h': False,
            '<endpoints>': endpoints,
            '<input>': input_file
        }

    def _test_excel_output(self, docopt_args):
        self.assertFalse(os.path.exists(self.output_excel_file))
        hc_api_export.hc_api_export(docopt_args)
        self.assertTrue(os.path.exists(self.output_excel_file))

    def _test_csv_output(self, docopt_args):
        self.assertFalse(os.path.exists(self.output_csv_path))
        hc_api_export.hc_api_export(docopt_args)
        self.assertTrue(os.path.exists(self.output_csv_path))

    def test_hc_api_export_property_excel(self):
        self._test_excel_output(self.get_docopt_args(
            'excel', 'property/*', './tests/test_files/test_input.csv'
        ))

    def test_hc_api_export_property_csv(self):
        self._test_csv_output(self.get_docopt_args(
            'csv', 'property/*', './tests/test_files/test_input.csv'
        ))

    def test_hc_api_export_excel_property_city_state(self):
        self._test_excel_output(self.get_docopt_args(
            'excel', 'property/*', './sample_input/sample-input-city-state.csv'
        ))

    def test_hc_api_export_csv_property_city_state(self):
        self._test_csv_output(self.get_docopt_args(
            'csv', 'property/*', './sample_input/sample-input-city-state.csv'
        ))

    def test_hc_api_export_excel_property_slug(self):
        self._test_excel_output(self.get_docopt_args(
            'excel', 'property/*', './sample_input/sample-input-slugs.csv'
        ))

    def test_hc_api_export_csv_property_slug(self):
        self._test_csv_output(self.get_docopt_args(
            'csv', 'property/*', './sample_input/sample-input-slugs.csv'
        ))

    def test_hc_api_export_zip_excel(self):
        self._test_excel_output(self.get_docopt_args(
            'excel', 'zip/*', './sample_input/sample-input-zipcodes.csv'
        ))

    def test_hc_api_export_zip_csv(self):
        self._test_csv_output(self.get_docopt_args(
            'csv', 'zip/*', './sample_input/sample-input-zipcodes.csv'
        ))

    def test_hc_api_export_block_excel(self):
        self._test_excel_output(self.get_docopt_args(
            'excel', 'block/*', './sample_input/sample-input-blocks.csv'
        ))

    def test_hc_api_export_block_csv(self):
        self._test_csv_output(self.get_docopt_args(
            'csv', 'block/*', './sample_input/sample-input-blocks.csv'
        ))

    def test_hc_api_export_msa_excel(self):
        self._test_excel_output(self.get_docopt_args(
            'excel', 'msa/*', './sample_input/sample-input-msas.csv'
        ))

    def test_hc_api_export_msa_csv(self):
        self._test_csv_output(self.get_docopt_args(
            'csv', 'msa/*', './sample_input/sample-input-msas.csv'
        ))

    def test_hc_api_export_property_single_endpoint(self):
        self._test_excel_output(self.get_docopt_args(
            'excel', 'property/value', './tests/test_files/test_input.csv'
        ))
