import unittest
from housecanary.excel import utilities


class ExcelUtilitiesTestCase(unittest.TestCase):
    """Tests for the Excel Utilities"""

    def test_normalize_cell_value_for_dict(self):
        result = utilities.normalize_cell_value({'test': 'value'})
        self.assertEqual('{"test": "value"}', result)

    def test_normalize_cell_value_for_list(self):
        result = utilities.normalize_cell_value([{'test1': 'value1'}, {'test2': 'value2'}])
        self.assertEqual('[{"test1": "value1"}, {"test2": "value2"}]', result)

    def test_normalize_cell_value_for_other_type(self):
        result = utilities.normalize_cell_value(5)
        self.assertEqual(5, result)

    def test_convert_snake_to_title_case(self):
        result = utilities.convert_snake_to_title_case('address_full_value')
        self.assertEqual('Address Full Value', result)

    def test_convert_title_to_snake_case(self):
        result = utilities.convert_title_to_snake_case('Address Full Value')
        self.assertEqual('address_full_value', result)

    def test_get_addresses_from_input_file(self):
        result = utilities.get_addresses_from_input_file('./tests/test_files/test_input.csv')
        self.assertEqual(('43 Valmonte Plaza', '90274'), result[0])
        self.assertEqual(('244 S ALTADENA DR', '91107'), result[1])

    def test_get_identifiers_from_input_file_with_extra_field(self):
        result = utilities.get_identifiers_from_input_file('./tests/test_files/test_input.csv')
        self.assertEqual({'zipcode': '90274', 'address': '43 Valmonte Plaza'}, result[0])
        self.assertEqual({'zipcode': '91107', 'address': '244 S ALTADENA DR'}, result[1])

    def test_get_identifiers_from_input_file_with_block_ids(self):
        result = utilities.get_identifiers_from_input_file('./sample_input/sample-input-blocks.csv')
        self.assertEqual({'property_type': 'SFD', 'block_id': '060376703241005'}, result[0])
        self.assertEqual({'property_type': 'SFD', 'block_id': '060374632002006'}, result[1])

    def test_get_identifiers_from_input_file_with_city_state(self):
        result = utilities.get_identifiers_from_input_file(
            './sample_input/sample-input-city-state.csv'
        )
        self.assertEqual(
            {'address': '43 Valmonte Plaza', 'city': 'Palos Verdes Estates', 'state': 'CA'},
            result[0]
        )
        self.assertEqual(
            {'address': '244 S ALTADENA DR', 'city': 'Pasadena', 'state': 'CA'},
            result[1]
        )

    def test_get_identifiers_from_input_file_with_msas(self):
        result = utilities.get_identifiers_from_input_file('./sample_input/sample-input-msas.csv')
        self.assertEqual({'msa': '31080'}, result[0])
        self.assertEqual({'msa': '29820'}, result[1])

    def test_get_identifiers_from_input_file_with_slugs(self):
        result = utilities.get_identifiers_from_input_file('./sample_input/sample-input-slugs.csv')
        self.assertEqual(
            {'client_value': '1000000',
             'client_value_sqft': '2000',
             'slug': '43-Valmonte-Plz-Palos-Verdes-Estates-CA-90274'},
            result[0]
        )
        self.assertEqual(
            {'client_value': '1200000',
             'client_value_sqft': '2500',
             'slug': '244-S-Altadena-Dr-Pasadena-CA-91107'},
            result[1]
        )

    def test_get_identifiers_from_input_file_with_zipcodes(self):
        result = utilities.get_identifiers_from_input_file('./sample_input/sample-input-zipcodes.csv')
        self.assertEqual({'meta': 'Area 1', 'zipcode': '90274'}, result[0])
        self.assertEqual({'meta': 'Area 2', 'zipcode': '91107'}, result[1])
