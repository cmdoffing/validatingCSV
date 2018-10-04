import sys
import unittest
sys.path.append('..')
import validatingCSV as vcsv


class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        rdr = vcsv.ValidatingCSVReader('../csvdata/pipes.csv',
                                       '../csvdata/pipeparams.json',
                                       error_file_path='../test/temp.errors')
        for row in rdr:
            print(row)
        err_string = ' '.join(rdr.errors)
        self.assertNotIn('Description is too long', err_string)
        self.assertIn('The length of value "MUST SELL! air, moon roof, loaded" is greater than max_len',
                      err_string)


if __name__ == '__main__':
    unittest.main()
