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

class CommandHelper:
    @staticmethod
    def support_command(command):
        supported = True
        command_name = command if isinstance(command, basestring) else command[0]
        try:
            CommandHelper.run_command(command)
            if glob.GlobalParams.is_debug():
                print '[DEBUG] Checking if '+command_name+' is available on system > True'
        except OSError:
            supported = False
            if glob.GlobalParams.is_debug():
                print '[DEBUG] Checking if '+command_name+' is available on system > False'
        return supported

    @staticmethod
    def run_command(command):
        subprocess.call(command)

    @staticmethod
    def run_command_async(command):
        subprocess.Popen(command)

    @staticmethod
    def strip_coloring(line):
        matches = re.findall('\[[0-9]+\w', line)
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