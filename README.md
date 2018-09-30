## validatingCSV: A Declarative, Validating CSV Reader Library For Python 3

### Overview

validatingCSV is a Python package for inputting and converting data from CSV iterables.
Use validatingCSV when your CSV data absolutely, positively has to be valid.
Which is pretty much always.

### Design Goals

validatingCSV has the following design goals:

* Maximum input validation. This is based on the developers long experience that
that bad input data is far more common that is usually supposed. We want to check the
input data in every way possible.

* Declarative specification. In general, declarative code has fewer bugs and is easier
to modify than functional, OOP, or imperative code. Let's do more of this.

* In particular, input validation should be as declarative as possible, even though validation
sometimes requires functional code. No OOP or imperative code should ever be necessary.

* It must be possible to specify more than one validator for each field.
This makes it easier to clarify intent, since each validator is doing exactly one (small) thing.

* Validation error messages should include the erroneous CSV row as well as all error
messages from all validators. These should be written to a text (utf-8) file if a path
for an error file is specified. It should also be easy to additionally write them to stderr.

* For elegance and efficiency, rows are returned as named tuples. These are the most natural
fit for CSV row output.

* Rows with invalid values should appear only in the error file, not in the output.

* It should be possible to generate named tuples easily with the names supplied by
the user in the input specification.

### Trade-offs

Since validatingCSV does everything the built-in csv module does and a lot more, it is naturally
going to be slower. This is a more than acceptable trade-off in most contexts, since getting
the wrong answer quickly isn't very useful. Programming is ultimately about data, and bad
data is worse than no data, especially when you don't know it's bad.

### Example Usage

```python
import sys
import validatingCSV as vcsv


readerParams = {'delimiter': '|', 'max_bad_rows': 100}


def description_is_invalid(field, field_validation_params):
    return 'Description is too long\n' if len(field) > 15 else None

def price_converter(field, base):
    return round(float(field))

def year_converter(field, base):
    return int(field, base)


year_validation   = {'name': 'year', 'desc': 'The year the car was made.',
                     'type': int, 'valid_values': [1996, 1997, 1998, 1999], 'converter': year_converter}
make_validation   = {'name': 'make', 'valid_values': set(['Ford', 'Chevy', 'Jeep'])}
model_validation  = {'name': 'model', 'min': 'AAA', 'max': 'zzz'}
desc_validation   = {'name': 'description', 'error_checker': description_is_invalid}
price_validation  = {'name': 'price', 'type': float, 'converter': price_converter}
validation_params = (year_validation, make_validation, model_validation, desc_validation, price_validation)


if __name__ == '__main__':
    filepath = sys.argv[1]
    rdr = vcsv.ValidatingCSVReader(filepath, readerParams, validation_params)
    for row in rdr:
        if row:
            print(row)

```

### CSV Iterable API

Fully specifying a validatingCSV reader requires defining two dicts: one for the
CSV file or other iterable as a whole and one for the fields in the rows.
This section defines the CSV iterable as a whole.
The Field Specification API further below describes how fields should be defined.

The validatingCSV reader uses Python's built-in csv module to perform reader 
operations on csv iterables. To do this, the validatingCSV module supplies any
parameters needed by the standard csv reader. Unsurprisingly then, the
CSV Iterable API precisely mirrors that of the Dialect class supplied to the
csv reader.

To specify parameters for the CSV iterable, define a dict that contains entries for
any of the parameters that need to be supplied to the csv reader, as defined in
the [documentation for the Dialect class](https://docs.python.org/3/library/csv.html#csv-fmt-params).
Most of what follows is a repetition of the information found there, except as marked below,
put here for convenience.

* 'delimiter' : A one-character string used to separate fields. It defaults to ','.

* 'doublequote' : Controls how instances of quotechar appearing inside a field should themselves be quoted. When True, the character is doubled. When False, the escapechar is used as a prefix to the quotechar. It defaults to True.

  * On output, if doublequote is False and no escapechar is set, Error is raised if a quotechar is found in a field.

* 'escapechar' : A one-character string used by the writer to escape the delimiter if quoting is set to QUOTE_NONE and the quotechar if doublequote is False. On reading, the escapechar removes any special meaning from the following character. It defaults to None, which disables escaping.

* 'lineterminator' : The string used to terminate lines produced by the writer. It defaults to '\r\n'. Note The reader is hard-coded to recognize either '\r' or '\n' as end-of-line, and ignores lineterminator. This behavior may change in the future.

* 'quotechar' : A one-character string used to quote fields containing special characters, such as the delimiter or quotechar, or which contain new-line characters. It defaults to '"'.

* 'quoting' : Controls when quotes should be generated by the writer
  and recognised by the reader. It can take on any of the QUOTE_* constants
  (see section Module Contents) and defaults to QUOTE_MINIMAL.

* 'skipinitialspace' : When True, whitespace immediately following the
  delimiter is ignored. The default is False.

* 'strict' : When True, raise exception Error on bad CSV input. The default is False.

The following parameters are used specifically by the validatingCSV module:

* 'fields': Required. The list of field definitions containing the validation parameters.
  There must be an entry in this list for every field in a row of the CSV file.

* 'max_bad_rows': Optional, defaults to 100.
  The maximum number of rows with errors that can occur before the iterator terminates.
  If this limit is exceeded a message similar to "101 bad CSV rows. max_bad_rows limit exceeded." is sent
  to stderr. Further processing is then terminated. This parameter is useful with large CSV files or for
  testing out validation parameters, where a mistake may cause every row to be marked as bad.


#### Field Specification API

Every row in a CSV iterable (except possibly the headers) has (or should have)
the same number of fields.
While the CSV Iterable API defines the parameters for the file or stream as a whole,
the row API allows you to define a name, validators, and data converters for each field.

A row specification consists of a sequence of either field specifications or falsy values,
with exactly one specification/falsy for each field in the row.
If you want to forgo validating, say, the third field, place a None or some other falsy
value in the third position of the validation parameters list.

If the rows have fields at the end that you want to ignore, you can forgo specifying
field validations for these. They will be ignored.

Since the API uses dictionaries to specify the fields.
All of the following attributes are optional except for 'name.'

Frequently, you will want to ignore the values from a given field.
To handle this case, place a falsy value (None is recommended) in the field specification.
The field will be ignored in all rows, saving processing time.

There are several kinds of validations that can be specified. They are done in the order
listed below. If any one of them fails, no further validations are done for that field
in the current row.

* 'name' : Every field spec should define a 'name' entry.
This will be used to create the field's name in the named tuple representing the row.
The name must be a valid Python identifier.

* 'desc' : A string describing the field. Useful for program documentation.

* 'type' : If present, this must be either 'integer', 'float', or 'complex'.
If not present, no check is done on the type of the field's
contents, since all fields are read in as strings. Forgoing a type check saves time.

* 'default' : The default value to return if the field is empty.

* 'base' : The base (radix) to by the int(num, base) function for integer conversions.
This must be either missing or one of the legal values for the base parameter, which
are 2 - 36.

* 'min' : The minimum value of the field. This can be an integer, a float, a complex number,
or a string. The standard Python comparison operator is used.
If the 'converter' parameter is present, the converter is called and its result value
is compared to the 'min' value.

* 'max' : The maximum value of a field. Similar considerations apply as for 'min'.

* 'valid_values' : An iterable containing only those values that are valid for this field.
If a non-string type is used, the field will first be converted to a value of that type
before this check is made.
Strings are checked directly against the values here.

* 'error_checker' : A user-defined function that is called with two parameters:
the original (string)
value of the field as the first parameter and the field_validation_params
 is the second.
Note that, if present, 'min', 'max', and/or 'valid_values' checks will still be done.
Return the error message as a string if there is an error, else return a falsy value.

* 'converter' : A user-defined function that is called with a two parameters:
the original (string) value of the field and a base value, to be used in case an
integer conversion is being done. It returns the converted value of the field,
which is then passed to the caller as the field's value.
