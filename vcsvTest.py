import sys
import validatingCSV
import params


if __name__ == '__main__':
    filepath = sys.argv[1]
    rdr = validatingCSV.ValidatingCSVReader(filepath,
                        params.readerParams, params.validation_params)
    for row in rdr:
        if row:
            print(row)

    print('\n---------- Errors -----------')
    for err in rdr.errors:
        print(err)
