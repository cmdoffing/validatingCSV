import csv
import sys
from collections import namedtuple


class ValidatingCSVReader:
    """
    A validating CSV reader with a declarative interface.
    Rows with bad data are written to an error file.
    """

    def __init__(self, csvfilepath, reader_params):
        self.errors = []

        self.num_bad_rows = 0
        max_bad_rows_param = 'max_bad_rows'
        self.max_bad_rows = reader_params.get(max_bad_rows_param, 100)
        if max_bad_rows_param in reader_params:
            del reader_params[max_bad_rows_param]

        try:
            validation_params_key = 'validation_params'
            self.row_validation_params = reader_params.get(validation_params_key, None)
            del reader_params[validation_params_key]
        except:
            sys.stderr.write('\n"validation_params" not found in parameters\n\n')
            raise

        self.csvfile = open(csvfilepath)
        self.csv_reader = csv.reader(self.csvfile, **reader_params)
        self.Row_tuple_type = self.make_row_tuple_type()

    def make_row_tuple_type(self):
        fieldnames = [d['name'] for d in self.row_validation_params if d]
        nmdtuple = namedtuple('RowTuple', fieldnames)
        return nmdtuple

    def __next__(self):
        try:
            row = next(self.csv_reader)    # returns a list of strings
        except:
            # This is the place to close the input file when we run out of records
            self.csvfile.close()
            raise StopIteration
        err_list, new_row = self.row_validator(row)
        if err_list:
            self.errors.extend(err_list)
            self.num_bad_rows += 1
            if self.num_bad_rows > self.max_bad_rows:
                sys.stderr.write(str(self.num_bad_rows) + " bad CSV rows. max_bad_rows limit exceeded.\n")
                raise StopIteration
            return
        else:
            return self.Row_tuple_type(*new_row)

    def __iter__(self):
        return self

    def validated_field(self, index):
        return self.row_validation_params[index]

    def row_validator(self, row):
        """
        Checks each row (which is a list of strings) against self.row_validation_params for errors.
        Returns an empty list if the row is valid, error info otherwise.
        If an error is found, add the row to the front of the list followed by all of the
        error messages from the row.
        The row param is checked against self.row_validation_params, which is a list of dicts
        of validation parameters.
        """

        err_list = []
        new_row  = []
        for i in range(0, len(row)):
            if self.validated_field(i):
                field = row[i]
                field_validation_params = self.row_validation_params[i]
            else:
                continue

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

            new_row.append(self.convert_value(field, field_validation_params))
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
