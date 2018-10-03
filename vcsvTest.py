import sys
import validatingCSV


if __name__ == '__main__':
    csv_file_path    = sys.argv[1]
    json_params_path = sys.argv[2]
    reader = validatingCSV.ValidatingCSVReader(csv_file_path, json_params_path,
                                               error_file_path='./test/temp.errors',
                                               log_file_path='vcsv.log')
    for row in reader:
        if row:
            print(row)

    print('\n---------- Errors -----------')
    for err in reader.errors:
        print(err)
