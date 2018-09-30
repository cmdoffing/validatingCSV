import unittest
import validatingCSV as vcsv
import params


class TestValidatingCSV(unittest.TestCase):

    def setUp(self):
        self.validating_reader = vcsv.ValidatingCSVReader('./csvdata/pipes.csv',
                                params.readerParams)

    def testUnitTest(self):
        self.assertEqual('A', 'A')


if '__name__' == '__main__':
    unittest.main()
