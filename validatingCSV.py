import csv
import sys
from collections import namedtuple


class ValidatingCSVReader:
    """
    A validating CSV reader with a declarative interface.
    Rows with bad data are written to an error file.
    """

    def __init__(self, csvfilepath, reader_params, row_validation_params):
        self.csvfile = open(csvfilepath)
        self.csv_reader = csv.reader(self.csvfile, **reader_params)
        self.error_file = open(csvfilepath + '.errors', 'w')
        self.row_validation_params = row_validation_params
        self.Row_tuple_type = self.make_row_tuple_type()

    def make_row_tuple_type(self):
        fieldnames = [d['name'] for d in self.row_validation_params]
        return namedtuple('RowTuple', fieldnames)

    def write_errors(self, errors):
        for err in errors:
            self.error_file.write(str(err))
        return

    def __next__(self):
        try:
            row = next(self.csv_reader)    # returns a list of strings
        except:
            # This is the place to close the files when we run out of records
            self.csvfile.close()
            self.error_file.close()
            raise StopIteration
        err_list, new_row = self.row_validator(row)
        if err_list:
            self.write_errors(err_list)
            return
        else:
            return self.Row_tuple_type(*new_row)

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

            range_error = self.range_error(field, field_validation_params)
            if range_error:
                err_list.append(range_error)

            error_checker_error = self.error_checker_error(field, field_validation_params)
            if error_checker_error:
                err_list.append(error_checker_error)

            # If an error has not yet occurred, include the row at the start of the error output.
            if type_error or valid_values_error or error_checker_error or range_error:
                err_list.insert(0, '\n\n' + str(row) + '\n')

            new_row[i] = self.convert_value(field, field_validation_params)
        return err_list, new_row

    def field_type_error(self, field, field_validation_params):
        if 'type' in field_validation_params:
            field_type = field_validation_params['type']
            # Check integer types
            if field_type == 'integer':
                try:
                    value = int(field)
                except ValueError:
                    return 'Value "' + field + '" is not an integer\n'
            # Check float types
            if field_type == 'float':
                try:
                    value = float(field)
                except ValueError:
                    return 'Value "' + field + '" is not an float\n'
            # Check complex types
            if field_type == 'complex':
                try:
                    value = complex(field)
                except ValueError:
                    return 'Value "' + field + '" is not an complex number\n'
        return

    def valid_values_error(self, field, field_validation_params):
        if 'valid_values' in field_validation_params:
            converted_value = self.convert_value(field, field_validation_params)
            if converted_value not in field_validation_params['valid_values']:
                return field + ' is not a valid value of the ' + field_validation_params['name'] + ' field\n'
        return

    def range_error(self, field, field_validation_params):
        converted_value = self.convert_value(field, field_validation_params)
        if 'min' in field_validation_params:
            min_value = field_validation_params['min']
            if converted_value < min_value:
                return 'Value "' + field + '" is less than the specified min value\n'
        if 'max' in field_validation_params:
            max_value = field_validation_params['max']
            if converted_value > max_value:
                return 'Value "' + field + '" is greater than the specified max value\n'

    def error_checker_error(self, field, field_validation_params):
        if 'error_checker' in field_validation_params:
            checker = field_validation_params['error_checker']
            error_str = checker(field, field_validation_params)
            if error_str:
                return error_str
        return

    def type_based_conversion(self, field, field_validation_params):
        type_converter = field_validation_params.get('converter', None)
        return type_converter(field) if type_converter else field

    def convert_value(self, field, field_validation_params):
        # Return default value for the field if it's an empty string
        if field == '':
            return field_validation_params.get('default', '')
        converter = field_validation_params.get('converter', None)
        # Including the field_validation_params in this call allows the converter
        # to use the base parameter for integer conversions plus any future parameters.
        base = field_validation_params.get('base', 10)
        return converter(field, base) if converter else field
