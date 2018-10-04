import csv
import json
import logging
import datetime
from collections import namedtuple
import vcsvUtils


class ValidatingCSVReader:
    """
    A validating CSV reader with a declarative interface.
    Rows with bad data are written to an error file.
    """

    def __init__(self, csv_file_path, json_params_filepath,
                 error_file_path=None, log_file_path=None):
        self.errors = []
        self.error_file_path = error_file_path

        with open(json_params_filepath) as json_file:
            reader_params = json.load(json_file)

        self.log_file_path = log_file_path
        if log_file_path:
            logging.basicConfig(filename=log_file_path, filemode='w',
                                level=logging.INFO)
            logging.info('Starting processing at ' + str(datetime.datetime.now()))
            logging.info(str(reader_params))

        self.num_bad_rows = 0
        max_bad_rows_param = 'max_bad_rows'
        self.max_bad_rows = reader_params.get(max_bad_rows_param, 100)

        validation_params_key = 'validation_params'
        try:
            self.row_validation_params = reader_params.get(validation_params_key, None)
        except:
            if self.log_file_path:
                logging.error(validation_params_key + ' entry not found in parameters file.')
            raise

        num_header_lines_key = 'num_header_lines'
        num_header_lines = reader_params.get(num_header_lines_key, 0)
        if num_header_lines <= 0:
            # Don't skip any lines if there are no header lines
            new_csv_path = csv_file_path
        else:
            new_csv_path = vcsvUtils.skip_n_lines_in_file(csv_file_path, num_header_lines)

        csv_reader_params = vcsvUtils.remove_items_from_dict(reader_params,
                                [max_bad_rows_param, validation_params_key,
                                 num_header_lines_key])
        self.csv_file = open(new_csv_path)
        self.csv_reader = csv.reader(self.csv_file, **csv_reader_params)
        self.Row_tuple_type = self.make_row_tuple_type()


    def make_row_tuple_type(self):
        fieldnames = [d['name'] for d in self.row_validation_params if d]
        return namedtuple('RowTuple', fieldnames)


    def __next__(self):
        try:
            row = next(self.csv_reader)    # returns a list of strings
        except:
            # This is the place to close the input file when we run out of
            # records and to write out any errors to the error file, which
            # handles errors as a batch.
            self.csv_file.close()
            if self.error_file_path:
                with open(self.error_file_path, 'w') as error_file:
                    error_file.writelines(self.errors)
            raise StopIteration

        # Now validate the row just retrieved from the CSV file
        new_row, err_list = self.row_validator(row)
        if not err_list:
            return self.Row_tuple_type(*new_row)
        else:
            self.errors.extend(err_list)
            if self.log_file_path:
                logging.warning(str(err_list))

            self.num_bad_rows += 1
            if self.num_bad_rows > self.max_bad_rows:
                max_errors_msg = str(self.num_bad_rows) + \
                                 " bad CSV rows. max_bad_rows limit exceeded."
                self.errors.append(max_errors_msg)
                if self.error_file_path:
                    with open(self.error_file_path, 'w') as error_file:
                        error_file.writelines(self.errors)
                if self.log_file_path:
                    logging.error(max_errors_msg)
                raise StopIteration
            return


    def __iter__(self):
        return self


    def add_error_to_list(self, row, error_list, err_string):
        # The return value must always include the CSV row as a string in the
        # first position. If there is already an error in the list then
        # we don't need to add it.
        row_list = [] if error_list else [str(row)]
        return error_list + row_list + [str(err_string)]


    def row_validator(self, row):
        """
        Checks each row (which is a list of strings) against
        self.row_validation_params for errors.
        Returns an empty list if the row is valid, error info otherwise.
        If an error is found, add the row to the front of the list
        followed by all of the error messages from the row.
        The row param is checked against self.row_validation_params, which is
        a list of dicts of validation parameters.
        """

        err_list = []
        new_row  = []
        for i in range(0, len(row)):
            # Fields that will not be validated are marked as None and will be ignored
            field_validation_params = self.row_validation_params[i]
            if field_validation_params:
                field = row[i]
                value, error_msg = self.converted_value(field, field_validation_params)
                if error_msg:
                    err_list = self.add_error_to_list(row, err_list, error_msg)
                    continue
            else:
                continue

            valid_values_error = self.valid_values_error(field, value, field_validation_params)
            if valid_values_error:
                err_list = self.add_error_to_list(row, err_list, valid_values_error)
                continue

            range_error = self.range_error(field, value, field_validation_params)
            if range_error:
                err_list = self.add_error_to_list(row, err_list, range_error)
                continue

            min_len_error = self.min_len_error(field, value, field_validation_params)
            if min_len_error:
                err_list = self.add_error_to_list(row, err_list, min_len_error)
                continue

            max_len_error = self.max_len_error(field, value, field_validation_params)
            if max_len_error:
                err_list = self.add_error_to_list(row, err_list, max_len_error)
                continue

            new_row.append(value)
        return new_row, err_list


    def converted_value(self, field, field_validation_params):
        # Returns a pair of the converted value, if no error, and an error message (or None).
        # If the field is an empty string, return the default value.
        # If no type param is present, default the field type to 'string'.

        field_type = field_validation_params.get('type', 'string')
        if field_type == 'string':
            if field != '':
                return (field, None)
            else:
                default = field_validation_params.get('default', None)
                if default:
                    return (default, None)
                else:
                    return (field, None)

        # This check has to come after the check for a field type of string,
        # since an empty string is a valid value for string fields but not
        # other types of fields.
        if field == '':
            default = field_validation_params.get('default', None)
            if default:
                return (default, None)
            else:
                return (None, 'Empty string cannot be converted to non-string types')

        if field_type == 'integer':
            try:
                base  = field_validation_params.get('base', 10)
                value = int(field, base)
                return (value, None)
            except ValueError:
                return (None, 'Value "' + field + '" is not an integer')

        if field_type == 'float':
            try:
                value = float(field)
                return (value, None)
            except ValueError:
                return (None, 'Value "' + field + '" is not a float')

        if field_type == 'complex':
            try:
                value = complex(field)
                return (value, None)
            except ValueError:
                return (None, 'Value "' + field + '" is not a complex number')

        return (None, '"type" parameter "' + field_type + '" is invalid')


    def valid_values_error(self, field, value, field_validation_params):
        valid_values = field_validation_params.get('valid_values', None)
        if valid_values and value not in valid_values:
                return field + ' is not a valid value of the ' + \
                       field_validation_params['name'] + ' field'
        return

    def range_error(self, field, value, field_validation_params):
        min_value = field_validation_params.get('min', None)
        if min_value and value < min_value:
            return 'Value "' + field + '" is less than the specified min value'

        max_value = field_validation_params.get('max', None)
        if max_value and value > max_value:
            return 'Value "' + field + '" is greater than the specified max value'

    def min_len_error(self, field, value, field_validation_params):
        min_len = field_validation_params.get('min_len', None)
        if min_len and len(value) < min_len:
            return 'The length of value "' + field + '" is less than min_len'

    def max_len_error(self, field, value, field_validation_params):
        max_len = field_validation_params.get('max_len', None)
        if max_len and len(value) > max_len:
            return 'The length of value "' + field + '" is greater than max_len'
