import sys
import validatingCSV


if __name__ == '__main__':
    filepath         = sys.argv[1]
    json_params_path = sys.argv[2]
    rdr = validatingCSV.ValidatingCSVReader(filepath, json_params_path,
                                            error_file_path='./test/temp.errors')

    print('\n')
    for row in rdr:
        if row:
            print(row)

    print('\n---------- Errors -----------')
    for err in rdr.errors:
        print(err)
