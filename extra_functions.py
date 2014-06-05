import re
import time
import glob
import os
import subprocess

__author__ = 'Robbin Tapper'


class FileHelper:
    @staticmethod
    def write_string_to_file(path_and_file, string):
        file = open(path_and_file, "w+")
        file.write(string)
        file.close()

    @staticmethod
    def get_file_contents(path_and_file):
        contents = None
        if FileHelper.does_file_exist(path_and_file):
            contents = open(path_and_file, 'r').read()
        return contents

    @staticmethod
    def does_file_exist(path_and_file):
        return os.path.exists(path_and_file)

    @staticmethod
    def remove_file(path_and_file):
        if FileHelper.does_file_exist(path_and_file):
            os.remove(path_and_file)


class CommandHelper:
    @staticmethod
    def support_command(command):
        supported = True
        command_name = command if isinstance(command, basestring) else command[0]
        try:
            CommandHelper.run_command(command)
            glob.Debug.debug('[DEBUG] Checking if ' + command_name + ' is available on system > True')
        except OSError:
            supported = False
            glob.Debug.debug('[DEBUG] Checking if ' + command_name + ' is available on system > False')
        return supported

    @staticmethod
    def run_command(command):
        fh = open("NUL", "w")
        subprocess.call(command, stdout=fh, stderr=fh)
        fh.close()

    @staticmethod
    def run_command_async(command):
        fh = open("NUL", "w")
        subprocess.Popen(command, stdout=fh, stderr=fh)
        fh.close()

    @staticmethod
    def strip_coloring(line):
        matches = re.findall('\033?\[[0-9]{1,2}m?', line)
        if matches is not None and isinstance(matches, basestring):
            matches = [matches]
        if matches is not None and len(matches) > 0:
            for match in matches:
                line = line.replace(match, '')
        return line


class TimeHelper:
    @staticmethod
    def has_time_passed(last_trigger, passed_time):
        current_time = int(time.time() * 1000)
        return current_time - passed_time >= last_trigger

    @staticmethod
    def get_time():
        return int(time.time() * 1000)


class ColorOutput:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'

    BLACK = '\033[30m'
    GRAY = '\033[37m'
    WHITE = '\033[97m'

    END = '\033[0m'

    RAINBOW_LIST = [RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN]

    rainbow_color_offset = 0

    @staticmethod
    def get_colored(text):
        if glob.GlobalParams.get_color() is not None:
            color = glob.GlobalParams.get_color().lower()
            text = CommandHelper.strip_coloring(text)
            if color != 'rainbow':
                color_prefix = ColorOutput.RED if color == 'red' else (ColorOutput.GREEN if color == 'green' else (
                    ColorOutput.YELLOW if color == 'yellow' else (ColorOutput.BLUE if color == 'blue' else (
                        ColorOutput.MAGENTA if color == 'magenta' else (
                            ColorOutput.CYAN if color == 'cyan' else (
                                ColorOutput.WHITE if color == 'white' else (
                                    ColorOutput.GRAY if color == 'gray' else ColorOutput.BLACK)))))))
                return color_prefix + text + ColorOutput.END
            else:
                output = ''
                offset = ColorOutput.rainbow_color_offset % len(ColorOutput.RAINBOW_LIST)
                for i in range(0, len(text), 1):
                    if text[i] == ' ':
                        offset += 1
                        output += ' '
                    else:
                        output += ColorOutput.RAINBOW_LIST[(i - offset) % len(ColorOutput.RAINBOW_LIST)] + text[i]
                        ColorOutput.rainbow_color_offset += 1
                output += ColorOutput.END
                return output
        else:
            return text
