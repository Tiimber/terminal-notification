import os

__author__ = 'Robbin Tapper'


class ExtraFileMethods:
    @staticmethod
    def write_string_to_file(path_and_file, string):
        file = open(path_and_file, "w+")
        file.write(string)
        file.close()

    @staticmethod
    def get_file_contents(path_and_file):
        contents = None
        if ExtraFileMethods.does_file_exist(path_and_file):
            contents = open(path_and_file, 'r').read()
        return contents

    @staticmethod
    def does_file_exist(path_and_file):
        return os.path.exists(path_and_file)
