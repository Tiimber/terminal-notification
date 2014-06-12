from __future__ import print_function
import platform
import extra_functions


class GlobalParams():
    debug = False
    mute = False
    growl = False
    only_sound = False
    no_sound = False
    mac_afplay = False
    win_sounder = None
    color = None

    @staticmethod
    def set_debug(debug):
        GlobalParams.debug = debug

    @staticmethod
    def is_debug():
        return GlobalParams.debug

    @staticmethod
    def set_mute(mute):
        GlobalParams.mute = mute

    @staticmethod
    def is_mute():
        return GlobalParams.mute

    @staticmethod
    def set_growl(growl):
        GlobalParams.growl = growl

    @staticmethod
    def prefer_growl():
        return GlobalParams.growl

    @staticmethod
    def set_only_sound(only_sound):
        GlobalParams.only_sound = only_sound

    @staticmethod
    def is_only_sound():
        return GlobalParams.only_sound

    @staticmethod
    def set_no_sound(no_sound):
        GlobalParams.no_sound = no_sound

    @staticmethod
    def is_no_sound():
        return GlobalParams.no_sound

    @staticmethod
    def set_afplay(afplay):
        GlobalParams.mac_afplay = afplay

    @staticmethod
    def use_afplay():
        return GlobalParams.mac_afplay

    @staticmethod
    def set_sounder(sounder):
        GlobalParams.win_sounder = sounder

    @staticmethod
    def get_sounder():
        return 'sounder.exe' if GlobalParams.win_sounder is None else GlobalParams.win_sounder

    @staticmethod
    def set_color(color):
        color_supported = True
        if Platform.is_windows():
            Debug.debug('[DEBUG] Trying to use color parameter on Windows - will check if colorama is installed')
            # Only supported in windows if colorama is installed...
            try:
                import colorama
                colorama.init()
            except ImportError:
                color_supported = False
        if color_supported:
            GlobalParams.color = color

        if Platform.is_windows():
            if color_supported:
                Debug.debug('[DEBUG] Colorama is installed and working correctly - congratulations, you know have colored output')
            else:
                Debug.debug('[DEBUG] Colorama couldn\'t be found in your system, you will not be able to use the benefits of the color parameter')

    @staticmethod
    def unset_color():
        if Platform.is_windows() and GlobalParams.color is not None:
            Debug.debug('[DEBUG] Unregistering colorama for colored output in console')
            try:
                import colorama
                colorama.deinit()
            except ImportError:
                pass

    @staticmethod
    def get_color():
        return GlobalParams.color

class Platform():
    platform = None

    @staticmethod
    def set_platform():
        Platform.platform = {'platformsystem': platform.system(), 'platformmacver': platform.mac_ver()}


    @staticmethod
    def get_platform():
        return Platform.platform

    @staticmethod
    def is_mac_10_8_plus():
        is_mac = Platform.is_mac()
        if is_mac:
            mac_version = Platform.platform['platformmacver'][0]
            mac_version_split = mac_version.split('.')
            is_mac_version_ok = (len(mac_version_split) >= 2 and int(mac_version_split[0]) == 10 and int(mac_version_split[1]) >= 8) or (len(mac_version_split) >= 1 and int(mac_version_split[0]) > 10)
            Debug.debug('[DEBUG] Mac version "'+mac_version+'" is 10.8 or later > '+str(is_mac_version_ok))
            if is_mac_version_ok:
                return True
        return False

    @staticmethod
    def is_mac():
        platform_system = Platform.platform['platformsystem']
        platform_mac_ver = Platform.platform['platformmacver'][0]
        is_system_mac = platform_system.lower() == 'darwin' and len(platform_mac_ver) > 0
        Debug.debug('[DEBUG] Checking if "'+ platform_system +'" with version "'+platform_mac_ver+'" is Mac OS > '+str(is_system_mac))
        return is_system_mac

    @staticmethod
    def is_linux_with_notify_send():
        is_linux = Platform.is_linux()
        if is_linux:
            # Check if the command is actually there
            notify_send_available = extra_functions.CommandHelper.support_command(['notify-send', '--version'])
            if notify_send_available:
                return True
        return False

    @staticmethod
    def is_linux():
        platform_system = Platform.platform['platformsystem']
        is_system_linux = platform_system.lower() == 'linux'
        Debug.debug('[DEBUG] Checking if "'+ platform_system +'" is Linux > '+str(is_system_linux))
        return is_system_linux

    @staticmethod
    def is_windows():
        platform_system = Platform.platform['platformsystem']
        is_system_windows = platform_system.lower() == 'windows'
        Debug.debug('[DEBUG] Checking if "'+ platform_system +'" is Windows > '+str(is_system_windows))
        return is_system_windows

    @staticmethod
    def get_command_line_merge_for_platform():
        if Platform.is_windows():
            return ' && '
        else:
            return ' ; '

class Hang():
    last_line_time = None
    last_lines = []
    # Make sure we don't go on storing old lines forever, it also makes hanging detection slow
    number_of_lines_cap = 100

    @staticmethod
    def update_last_time():
        Hang.last_line_time = extra_functions.TimeHelper.get_time()

    @staticmethod
    def get_elapsed():
        now = extra_functions.TimeHelper.get_time()
        return now - Hang.last_line_time

    @staticmethod
    def add_line(line):
        Hang.last_lines.insert(0, line)
        if len(Hang.last_lines) > Hang.number_of_lines_cap:
            Hang.last_lines = Hang.last_lines[:Hang.number_of_lines_cap]

    @staticmethod
    def get_lines():
        return Hang.last_lines

class Debug():
    @staticmethod
    def debug(text):
        if GlobalParams.is_debug():
            print(extra_functions.ColorOutput.get_colored(text))
