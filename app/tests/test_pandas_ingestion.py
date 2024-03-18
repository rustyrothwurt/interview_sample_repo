import unittest
import os

from pandas import errors as pe
from services import ingestion as ig

class IngestionTestCase(unittest.TestCase):
    def setUp(self):
        dirname = os.path.dirname(__file__)
        self.file1 = os.path.join(dirname, 'resources/ingestion_test_1.csv')
        self.file1_result = [20090101, 20090102, 20090103, 20090105, 20090107, 20090109]
        self.file2 = os.path.join(dirname, 'resources/ingestion_test_2.csv')
        self.file2_error = "ValueError: {'value_validation': {'message': 'The input file has bad values', 'data': [{0: nan}]}}"
        self.file3 = os.path.join(dirname, 'resources/ingestion_test_3.csv')
        self.file3_error = "ValueError: {'value_validation': {'message': 'The input file has bad values', 'data': [{0: nan}, {1: nan}]}, 'column_validation': {'message': 'The input file has too many columns: 2', 'data': [0, 1]}}"
        self.file4 = os.path.join(dirname, 'resources/ingestion_test_4.csv')  # pandas.errors.ParserError
        self.file5 = os.path.join(dirname, 'resources/ingestion_test_5.csv')  # pandas.errors.EmptyDataError
        self.file6 = os.path.join(dirname, 'resources/ingestion_test_nothere.csv')  # FileNotFoundError
        self.file7 = os.path.join(dirname, 'resources/flask.png')  # UnicodeDecodeError

    def test_default_ingestion(self):
        self.assertEqual(ig.convert_csv_to_list(self.file1), self.file1_result,'csv ingestion broken for good file')

    def test_bad_ingestion_value_error(self):
        with self.assertRaises(ValueError):
            ig.convert_csv_to_list(self.file2)
        with self.assertRaises(ValueError):
            ig.convert_csv_to_list(self.file3)

    def test_bad_ingestion_parser_error(self):
        with self.assertRaises(pe.ParserError):
            ig.convert_csv_to_list(self.file4)

    def test_bad_ingestion_empty_error(self):
        with self.assertRaises(pe.EmptyDataError):
            ig.convert_csv_to_list(self.file5)

    def test_bad_ingestion_file_error(self):
        with self.assertRaises(FileNotFoundError):
            ig.convert_csv_to_list(self.file6)

    def test_bad_ingestion_decode_error(self):
        with self.assertRaises(UnicodeDecodeError):
            ig.convert_csv_to_list(self.file7)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
