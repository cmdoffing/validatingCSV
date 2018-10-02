import unittest
import validatingCSV as vcsv
import pipeparams as params


class TestValidatingCSV_Pipes(unittest.TestCase):

    def setUp(self):
        self.rdr = vcsv.ValidatingCSVReader('./csvdata/pipes.csv',
                                params.readerParams)
        self.err_string = ' '.join(self.rdr.errors)

    def test_description_too_long(self):
        self.assertIn('Description is too long', self.err_string)

    def test_description_too_long(self):
        self.assertIn('3 bad CSV rows.', self.err_string)


class TestValidatingCSV_Cars(unittest.TestCase):

    def setUp(self):
        self.rdr = vcsv.ValidatingCSVReader('./csvdata/cars.csv',
                                params.readerParams)
        self.err_string = ' '.join(self.rdr.errors)

    def test_description_too_long(self):
        self.assertIn('Description is too long', self.err_string)

    def test_description_too_long(self):
        self.assertIn('3 bad CSV rows.', self.err_string)


if '__name__' == '__main__':
    unittest.main()
