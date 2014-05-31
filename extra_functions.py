import os

__author__ = 'Robbin Tapper'


class ExtraFileMethods:
    @staticmethod
    def WriteStringToFile(pathAndFile, string):
        file = open(pathAndFile, "w+")
        file.write(string)
        file.close()

    @staticmethod
    def GetFileContents(pathAndFile):
        contents = None
        if ExtraFileMethods.DoesFileExist(pathAndFile):
            contents = open(pathAndFile, 'r').read()
        return contents

    @staticmethod
    def DoesFileExist(pathAndFile):
        return os.path.exists(pathAndFile)
