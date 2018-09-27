import sys
import validatingCSV as vcsv


readerParams = {'delimiter': '|'}

year_validation   = {'name': 'year'}
make_validation   = {'name': 'make'}
model_validation  = {'name': 'model'}
desc_validation   = {'name': 'description'}
price_validation  = {'name': 'price'}
validation_params = [year_validation, make_validation, model_validation, desc_validation, price_validation]


if __name__ == '__main__':
    filepath = sys.argv[1]
    with open(filepath) as csvfile:
        rdr = vcsv.ValidatingCSVReader(csvfile, readerParams, validation_params)
        for row in rdr:
            print(row)
