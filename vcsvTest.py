import sys
import validatingCSV
import pipeparams


if __name__ == '__main__':
    filepath   = sys.argv[1]
    rdr = validatingCSV.ValidatingCSVReader(filepath, pipeparams.readerParams,
                                            error_file_path='./test/temp.errors')
    print('\n')
    for row in rdr:
        if row:
            print(row)

    print('\n---------- Errors -----------')
    for err in rdr.errors:
        print(err)
