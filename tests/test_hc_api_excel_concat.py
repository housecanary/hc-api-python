import unittest
import requests_mock
import os
import io
import shutil
from housecanary.hc_api_excel_concat import hc_api_excel_concat


class HcApiExcelConcatTestCase(unittest.TestCase):
    """Tests for the hc_api_excel_concat tool"""

    def setUp(self):
        self.output_file = 'unittest_hc_api_excel_concat.xlsx'
        self.output_path = 'unittest_housecanary_excel'
        self._remove_test_output()
        self.headers = {"content-type": "application/xlsx"}

    def tearDown(self):
        self._remove_test_output()

    def _remove_test_output(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
        if os.path.exists(self.output_path):
            shutil.rmtree(self.output_path)

    def get_docopt_args(self, endpoint):
        return {
          '--endpoint': endpoint,
          '--files': self.output_path,
          '--help': False,
          '--key': None,
          '--output': self.output_file,
          '--retry': False,
          '--secret': None,
          '--type': None,
          '-h': False,
          '<input>': './tests/test_files/test_input.csv'
        }

    def test_hc_api_excel_concat_value_report(self):
        with io.open('tests/test_files/test_excel.xlsx', 'rb') as f:
            content = f.read()
        with requests_mock.Mocker() as m:
            m.get("/v2/property/value_report", headers=self.headers, content=content)
            self.assertFalse(os.path.exists(os.path.join(self.output_path, self.output_file)))
            self.assertFalse(os.path.exists(self.output_path))
            hc_api_excel_concat.hc_api_excel_concat(self.get_docopt_args('value_report'))
            self.assertTrue(os.path.exists(os.path.join(self.output_path, self.output_file)))
            self.assertTrue(os.path.exists(self.output_path))

    def test_hc_api_excel_concat_rental_report(self):
        with io.open('tests/test_files/test_excel.xlsx', 'rb') as f:
            content = f.read()
        with requests_mock.Mocker() as m:
            m.get("/v2/property/rental_report", headers=self.headers, content=content)
            self.assertFalse(os.path.exists(os.path.join(self.output_path, self.output_file)))
            self.assertFalse(os.path.exists(self.output_path))
            hc_api_excel_concat.hc_api_excel_concat(self.get_docopt_args('rental_report'))
            self.assertTrue(os.path.exists(os.path.join(self.output_path, self.output_file)))
            self.assertTrue(os.path.exists(self.output_path))
