
def skip_n_lines_in_file(file_path, num_lines):
    """
    Remove the initial num_lines of text from a file.

    :param file_path: The path to the file that needs initial lines removed.
    :param num_lines: The number of initial text lines to remove from the file
                      at file_path.
    :return: The path to a new temporary file that is the same as the file at
             file_path, except with the initial num_lines of text removed.

    Create a temporary text file. Give it a '.txt' extension since all we can
    assume about it is that it is a text file.
    Open file_path, read num_lines from it without copying any, then read the
    rest of the lines from the file and write them to the temp file.
    Close the temp file and return the path to it.
    """
    temp_file_path = '__temp_skipped_lines_file__.txt'
    temp_file = open(temp_file_path, 'w')
    with open(file_path) as orig_file:
        for i in range(0, num_lines):
            orig_file.readline()
        for line in orig_file:
            temp_file.write(line)
    temp_file.close()
    return temp_file_path


def remove_items_from_dict(a_dict, bad_keys):
    """
    Remove any items from a_dict whose keys are in bad_keys.

    :param a_dict: The dict to have keys removed from.
    :param bad_keys: The keys to remove from a_dict.
    :return: A copy of a_dict with the bad_keys items removed.
    """
    new_dict = {}
    for k in a_dict.keys():
        if k not in bad_keys:
            new_dict[k] = a_dict[k]
    return new_dict