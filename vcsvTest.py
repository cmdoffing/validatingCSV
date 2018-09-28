import sys
import validatingCSV as vcsv


readerParams = {'delimiter': '|'}


def description_is_invalid(field):
    return 'Description is too long' if len(field) > 15 else None

def price_converter(field, base=10):
    return round(float(field))

def year_converter(field, base):
    return int(field, base)


year_validation   = {'name': 'year', 'desc': 'The year the car was made.',
                     'type': 'integer', 'converter': int, 'base': 10, 'min': 1999, 'max': 2020}
make_validation   = {'name': 'make', 'valid_values': ['Ford', 'Chevy', 'Jeep']}
model_validation  = {'name': 'model'}
desc_validation   = {'name': 'description', 'error_checker': description_is_invalid,
                     'default': '***'}
price_validation  = {'name': 'price', 'type': 'float', 'converter': price_converter}
validation_params = (year_validation, make_validation, None, desc_validation, price_validation)


if __name__ == '__main__':
    filepath = sys.argv[1]
    rdr = vcsv.ValidatingCSVReader(filepath, readerParams, validation_params)
    for row in rdr:
        if row:
            print(row)
