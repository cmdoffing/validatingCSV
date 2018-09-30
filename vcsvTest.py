import sys
import validatingCSV
import params


if __name__ == '__main__':
    filepath = sys.argv[1]
    rdr = validatingCSV.ValidatingCSVReader(filepath, params.readerParams)
    for row in rdr:
        if row:
            print(row)

    print('\n---------- Errors -----------')
    for err in rdr.errors:
        print(err)
