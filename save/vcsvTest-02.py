import sys
import validatingCSV as vcsv


readerParams = {'delimiter': '|'}


def description_is_invalid(field):
    return 'Description is too long' if len(field) > 15 else None

def price_converter(field, base):
    return round(float(field))


year_validation   = {'name': 'year', 'desc': 'The year the car was made.',
                     'type': int}
make_validation   = {'name': 'make', 'valid_values': ['Ford', 'Chevy', 'Jeep']}
model_validation  = {'name': 'model'}
desc_validation   = {'name': 'description', 'error_checker': description_is_invalid}
price_validation  = {'name': 'price', 'type': float, 'converter': price_converter}
validation_params = (year_validation, make_validation, model_validation, desc_validation, price_validation)


if __name__ == '__main__':
    filepath = sys.argv[1]
    rdr = vcsv.ValidatingCSVReader(filepath, readerParams, validation_params)
    for row in rdr:
        if row:
            print(row)
