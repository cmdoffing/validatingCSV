import csv
import sys
from collections import namedtuple


class ValidatingCSVReader:
    """
    A validating CSV reader with a declarative interface.
    Rows with bad data are written to an error file.
    """

    def __init__(self, csvfile, reader_params, row_validation_params):
        self.csvfile    = csvfile
        self.csv_reader = csv.reader(csvfile, **reader_params)
        self.row_validation_params = row_validation_params
        self.row_tuple_type = self.make_row_tuple_type()
        #self.err_file_path  = err_file_path

    def make_row_tuple_type(self):
        fieldnames = [d['name'] for d in self.row_validation_params]
        return namedtuple('RowTuple', fieldnames)

    def write_errors(self, errors):
        for err in errors:

            #sys.stderr.write(str(err) + '\n')
        return

    def __next__(self):
        row = next(self.csv_reader)    # returns a list of strings
        err_list, new_row = self.row_validator(row)
        if err_list:
            self.write_errors(err_list)
            return
        else:
            return self.row_tuple_type(*new_row)

    def __iter__(self):
        return self

    def row_validator(self, row):
        """
        Checks each row (which is a list of strings) against self.params for errors.
        Returns an empty list if the row is valid, error info otherwise.
        If an error is found, add the row to the front of the list followed by all of the
        error messages from the row.
        The row param is checked against self.row_validation_params, which is a list of dicts
        of validation parameters.
        """
        err_list = []
        new_row = row.copy()
        for i in range(0, len(row)):
            field = row[i]
            field_validation_params = self.row_validation_params[i]

            type_error = self.field_type_error(field, field_validation_params)
            if type_error:
                err_list.append(type_error)

            valid_values_error = self.valid_values_error(field, field_validation_params)
            if valid_values_error:
                err_list.append(valid_values_error)

            error_checker_error = self.error_checker_error(field, field_validation_params)
            if error_checker_error:
                err_list.append(error_checker_error)

            # If an error has not yet occurred, include the row at the start of the error output.
            if err_list:
                err_list.insert(0, '------\n' + str(row))

            new_row[i] = self.convert_value(field, field_validation_params)
        return err_list, new_row

    def field_type_error(self, field, field_validation_params):
        if 'type' in field_validation_params:
            field_type = field_validation_params['type']
            try:
                value = field_type(field)
            except ValueError:
                return field + ' is not a valid instance of ' + field_type.__name__
        return

    def valid_values_error(self, field, field_validation_params):
        if 'valid_values' in field_validation_params:
            if field not in field_validation_params['valid_values']:
                return field + ' is not a valid value of the ' + field_validation_params['name'] + ' field'
        return

    def error_checker_error(self, field, field_validation_params):
        if 'error_checker' in field_validation_params:
            checker = field_validation_params['error_checker']
            error_str = checker(field)
            if error_str:
                return error_str
        return

    def convert_value(self, field, field_validation_params):
        converter = field_validation_params.get('converter', None)
        if converter:
            return converter(field)
        else:
            return field