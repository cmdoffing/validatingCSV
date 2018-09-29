import sys
import validatingCSV as vcsv


readerParams = {'delimiter': '|'}


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
