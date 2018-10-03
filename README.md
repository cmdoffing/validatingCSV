## validatingCSV: A Declarative, Validating CSV Reader Library For Python 3

### Overview

validatingCSV is a Python module for reading, converting, and validating
data from CSV files. It consists of a single class, ValidatingCSVReader,
which when instantiated returns an iterator that
returns one row of data at a time. Each row is represented as a named tuple,
with the field names of the named tuple supplied as part of the validation
parameters. The reader instance raises the standard StopIteration exception
(as do the built-in Python iterators) when it attempts to read the last
CSV row.

validatingCSV reads its validation and conversion parameters from a JSON file
and outputs any errors to an instance attribute of the ValidatingCSVReader
class. The user can also specify an optional error_file_path parameter
when instancing the class to hold errors.


### Design Goals

validatingCSV has the following design goals:

* Maximum declarative input validation.
This is based on the developer's long
experience that that bad input data is far more common that is usually
supposed. We want to check the input data in every declarative way possible.

* Declarative specification using JSON.
In general, declarative code has fewer bugs
and is easier to modify than functional, OOP, or imperative code.
This conflicts with the first goal,
since the JSON representation of the parameters cannot represent functions,
which limits some corner cases of validation.
This does make the validation interface much simpler.

* It must be possible to specify more than one validator for each field.
This makes it easier to clarify intent, since each validator is doing
exactly one (small) thing.

* Validation error messages should include the erroneous CSV row as well
as the error message. Having these together in one place greatly
simplifies finding the problem. These should be written to a
text (utf-8) file if a path for an error file is specified. It should
also be possible to retrieve them from a reader attribute.

* For elegance and efficiency, rows are returned as named tuples.
These are the most natural representation for CSV row output and allow
users of the validator to access fields by name in addition to position,
which reduces bugs and improves program readability.

* It should be possible to generate named tuples easily with the names
supplied by the user in the input specification.

* Rows with invalid values should appear only in the error lists,
not in the output.

* There should be multiple ways of obtaining error messages and a way
to limit the total number of error messages.


### Example Usage

```python
import sys
import validatingCSV


if __name__ == '__main__':
    csv_file_path    = sys.argv[1]
    json_params_path = sys.argv[2]
    reader = validatingCSV.ValidatingCSVReader(csv_file_path, json_params_path,
                                               error_file_path='./test/temp.errors')
    for row in reader:
        if row:
            print(row)

    print('\n---------- Errors -----------')
    for err in reader.errors:
        print(err)
```


### Example CSV Data

```
1997|Ford|E350|ac, abs, moon|3000.00
1999|Chevy|Venture Extended Edition||4900.00
1996|Jeep|Grand Cherokee|MUST SELL! air, moon roof, loaded|4799.00
1999|Chevy|Venture Extended Edition, Very Large||5000.00
```


### Example Parameter File

```javascript
{
"delimiter": "|",
"max_bad_rows": 2,
"validation_params": [
    {
        "name": "year",
        "desc": "The year the car was made.",
        "type": "integer",
        "valid_values": [1996, 1998, 1999]
    },
    null,
    null,
    {
        "name": "description",
        "min_len": 5,
        "max_len": 15
    },
    {
        "name": "price",
        "type": "float",
        "min" : 4000.00,
        "max" : 4950.00
    }
]
}
```


### Trade-offs

Since validatingCSV does everything the built-in csv module does and a
lot more, it is naturally going to be slower.
This is a more than acceptable trade-off in most contexts, since getting
the wrong answer quickly isn't very useful. Programming is ultimately
about data, and bad data is worse than no data, especially when you don't
know it's bad.


### CSV Reader Parameters

The validatingCSV module uses Python's built-in csv module to read the
CSV data from a file, one row at a time.
Once a row is read in, validation is applied according to the
parameters supplied in the validation parameters file.

Fully specifying a validatingCSV reader requires defining parameters for
Python's csv module as well as parameters specific to the validatingCSV
module.
The parameters work at two levels: the CSV file reader level and the
validation and conversion parameters for the individual fields.
This section covers the top-level (reader) parameters.
The Field Specification API further below describes how fields should be defined.

The validatingCSV reader uses Python's built-in csv module to perform reader 
operations on csv iterables. To do this, the validatingCSV module supplies any
parameters needed by the standard csv reader. Unsurprisingly then, the
CSV reader parameters listed below closely mirror that supplied to the
csv reader.

To specify parameters for the CSV iterable, define a JSON object in the
JSON parameters file that contains entries for
any of the parameters that need to be supplied to the csv reader, as
defined in the
[documentation for the Dialect class](https://docs.python.org/3/library/csv.html#csv-fmt-params).
Most of what follows is a repetition of the information found there,
except as otherwise marked, put here for convenience.

* 'delimiter' : A one-character string used to separate fields.
  It defaults to ','.

* 'doublequote' : Controls how instances of quotechar appearing inside a
   field should themselves be quoted. When True, the character is doubled.
   When False, the escapechar is used as a prefix to the quotechar.
   It defaults to True.

  * On output, if doublequote is False and no escapechar is set, Error
    is raised if a quotechar is found in a field.

* 'escapechar' : A one-character string used by the writer to escape the
  delimiter if quoting is set to QUOTE_NONE and the quotechar if
  doublequote is False. On reading, the escapechar removes any special
  meaning from the following character. It defaults to None, which
  disables escaping.

* 'lineterminator' : The string used to terminate lines produced by the
   writer. It defaults to '\r\n'. Note The reader is hard-coded to
   recognize either '\r' or '\n' as end-of-line, and ignores lineterminator.
   This behavior may change in the future.

* 'quotechar' : A one-character string used to quote fields containing
  special characters, such as the delimiter or quotechar, or which contain
  new-line characters. It defaults to '"'.

* 'quoting' : Controls when quotes should be generated by the writer
  and recognised by the reader. It can take on any of the QUOTE_* constants
  (see section Module Contents) and defaults to QUOTE_MINIMAL.
  Note that QUOTE_NONNUMERIC will convert unquoted fields into floats.
  This will interfere will data conversion done in the validator (which
  expects that all fields passed to it to be strings). Do not use
  this parameter constant with validatingCSV.

* 'skipinitialspace' : When True, whitespace immediately following the
  delimiter is ignored. The default is False.

* 'strict' : When True, raise exception Error on bad CSV input.
  The default is False.

The following parameters are used specifically by the validatingCSV
module and not by the underlying built-in csv module:

* 'fields': Required. The list of field definitions containing the
  validation parameters, as defined below. There must be an entry in
  this list for every field in a row of the CSV file, even if the entry
  is None for fields that are ignored.

* 'max_bad_rows': Optional, defaults to 100.
  The maximum number of rows with errors that can occur before the
  iterator terminates. If this limit is exceeded a message similar to
  "101 bad CSV rows. max_bad_rows limit exceeded." is output.
  Further processing is then terminated. This parameter is useful with
  large CSV files or for testing out validation parameters, where a
  parameter mistake may cause every row to be marked as bad.

* 'num_header_lines' : The number of header lines to ignore before
  retrieving the CSV rows as data. If you have header lines with fields
  to be converted to numbers, you will almost certainly get errors
  since the validator will try to convert the strings in the headers to
  numbers.


#### Field Parameters

Every row in a CSV iterable should have the same number of fields.
While the CSV Iterable Parameters defines the parameters for the file or
stream as a whole, the row API allows you to define a name, validators,
and data converters for each field.

A row specification consists of a sequence of either field specifications
or falsy values, with exactly one specification/falsy for each field in
the row.
If you want to forgo validating, say, the third field, place a None
(recommended) or some other falsy value in the third position of the
validation parameters list.

All of the following attributes are optional except for 'name.'

There are several kinds of validations that can be specified.
They are done in the order listed below.
If any one of them fails, no further validations are done for that field
in the current row.

* 'name' : Required, since the named tuple will be created using this name.
  The name must be a valid Python identifier.

* 'desc' : A string describing the field. Useful for documenting your
  validation process but otherwise unused by the program.

* 'type' : If present, this must be either 'integer', 'float', 'complex'
  or 'string'. If not present, the type defaults to 'string'.
  No conversion is done on 'string' types.
  'integer', 'float', and 'complex' types are converted before being
  placed in the named tuple for the row.

* 'default' : The default value to return if the field is empty.
  If a field is empty and no default is defined, an error is generated
  since an empty value for a non-string field type cannot be converted
  to a number.

* 'base' : The base (radix) to be used by the int(num, base) function for
  integer conversions. This must be either absent or one of the legal
  values for the base parameter, which are 2 - 36. Defaults to 10.

* 'min' : The minimum value of the field. This can be an integer, a float,
  or a string. Note that magnitude comparisons are not defined for
  complex numbers. The standard Python comparison operator
  is used. Field conversion is done before the 'min' check is done and
  the converted value is used for the comparison.

* 'max' : The maximum value of a field. Similar considerations apply as
  for 'min'.

* 'min_len' : The minimum allowed length of a string field.
  If not present there is no check on minimum length.
  Should not be used for non-'string' field types.

* 'max_len' : The maximum allowed length of a string field.
  If not present there is no check on maximum length.
  Should not be used for non-'string' field types.

* 'valid_values' : An iterable containing only those values that are
  valid for this field. If a non-string type is used, the field will
  first be converted to a value of that type before this check is made.
