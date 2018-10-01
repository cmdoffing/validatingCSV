import unittest
import validatingCSV as vcsv
import params

class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')
        rdr = vcsv.ValidatingCSVReader('./csvdata/pipes.csv',
                                            params.readerParams)
        err_string = ' '.join(rdr.errors)
        self.assertIn('Description is too long', err_string)

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()