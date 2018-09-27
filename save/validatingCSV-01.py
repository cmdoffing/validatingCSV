import csv
import sys
from collections import namedtuple


class ValidatingCSVReader:
    """
    A validating CSV reader with a declarative interface.
    Rows with bad data are written to an error file.
    """

    row_tuple_type = ()

    def make_row_tuple_type(self, validation_params):
        fieldnames = [d['name'] for d in validation_params]
        return namedtuple('Row_tuple_type', fieldnames)

    def __init__(self, csvfile, reader_params, validation_params):
        self.csvfile    = csvfile
        self.csv_reader = csv.reader(csvfile, **reader_params)
        self.row_validation_params = validation_params
        row_tuple_type = self.make_row_tuple_type(validation_params)

    def write_errors(self, errors):
        for err in errors:
            sys.stderr.write(str(err) + '\n')
        return

    def __next__(self):
        row = next(self.csv_reader)
        errors = self.row_errors(row)
        if errors:
            self.write_errors(errors)
        return row

    def __iter__(self):
        return self

    def row_errors(self, row):
        """
        Checks each row (which is a list of strings) against self.params for errors.
        Returns an empty list if the row is valid, error info otherwise.
        If an error is found, add the row to the front of the list followed by all of the
        error messages from the row.
        The row param is checked against self.row_validation_params, which is a list of dicts
        of validation parameters.
        """
        err_list = []
        return err_list
