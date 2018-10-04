import sys
import unittest
sys.path.append('..')
import validatingCSV as vcsv


temp_file_path = '__temp_skipped_lines_file__.txt'


class TestPipeCsvFile(unittest.TestCase):

    def setUp(self):
        temp_file = open(temp_file_path)
        temp_file.close()
        rdr = vcsv.ValidatingCSVReader('../csvdata/pipes.csv',
                                       '../csvdata/pipeparams.json',
                                       error_file_path='../test/temp.errors')
        self.row_count = 0
        for row in rdr:
            if row:
                self.row_count += 1
        self.err_string = ' '.join(rdr.errors)


    def test_pipes_no_rows_passed(self):
        self.assertEqual(self.row_count, 0, 'All rows should fail validation')

    def test_pipes_csv_error_msgs(self):
        self.assertNotIn('Description is too long', self.err_string)
        self.assertIn('1997 is not a valid value of the Year field', self.err_string)
        self.assertIn('Value "3000.00" is less than the specified min value',
                      self.err_string)
        self.assertIn('The length of value "" is less than min_len', self.err_string)
        self.assertIn('The length of value "MUST SELL! air, moon roof, loaded" is greater than max_len',
                      self.err_string)
        self.assertIn('Value "5000.00" is greater than the specified max value',
                      self.err_string)


class TestCarsCsvFile(unittest.TestCase):

    def setUp(self):
        temp_file = open(temp_file_path)
        temp_file.close()
        log_file_path = 'cars.log'
        rdr = vcsv.ValidatingCSVReader('../csvdata/cars.csv',
                                       '../csvdata/carsparams.json',
                                       error_file_path='cars.errors',
                                       log_file_path=log_file_path)
        self.row_count = 0
        self.tuples = []
        for row in rdr:
            if row:
                self.row_count += 1
                self.tuples.append(row)
        self.err_string = ' '.join(rdr.errors)

        # Get the log file lines
        with open(log_file_path) as log_file:
            self.log_file_lines = log_file.readlines()

        # Get the error file lines
        with open('cars.errors') as error_file:
            self.error_file_lines = error_file.readlines()


    def test_cars_log_file(self):
        self.assertIn('INFO:root:Starting processing at ', self.log_file_lines[0])
        self.assertIn("INFO:root:{'delimiter': ',', 'max_bad_rows': 2",
                      self.log_file_lines[1])
        self.assertIn("Ford is not a valid value of the Make field",
                      self.log_file_lines[2])

    def test_cars_num_rows_passed(self):
        self.assertEqual(self.row_count, 3, '3 rows should pass validation')

    def test_cars_csv_error_msgs(self):
        self.assertIn('Ford is not a valid value of the Make field',
                      self.err_string)

    def test_cars_error_file_msgs(self):
        self.assertEqual(1, len(self.error_file_lines))
        self.assertIn("['1997', 'Ford', 'E350', 'ac, abs, moon', '3000.00']Ford is not a valid value of the Make field",
                      self.error_file_lines[0])

    def test_cars_first_row_values(self):
        row = self.tuples[0]
        self.assertEqual(row.Year, 1999, 'Year must be 1999 for first row')
        self.assertEqual(row.Make, 'Chevy', 'Make must be Chevy for first row')
        self.assertEqual(row.Model, 'Venture Extended Edition', 'Model must be present for first row')
        self.assertEqual(row.Description, 'No description given',
                                          'Description must be default for first row')
        row = self.tuples[2]
        self.assertEqual(row.Year, 1996, 'Year must be 1999 for third row')
        self.assertEqual(row.Make, 'Jeep', 'Make must be Jeep for third row')
        self.assertEqual(row.Model, 'Grand Cherokee', 'Model must be present for third row')
        self.assertEqual(row.Description, 'MUST SELL! air, moon roof, loaded',
                                          'Description must be present for third row')


if __name__ == '__main__':
    unittest.main()
