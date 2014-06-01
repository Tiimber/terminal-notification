import platform
import extra_functions


class GlobalParams():
    debug = False
    mute = False
    growl = False

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


class Platform():
    platform = None

    @staticmethod
    def set_platform():
        Platform.platform = {'platformsystem': platform.system(), 'platformmacver': platform.mac_ver()}
        if GlobalParams.is_debug():
            print '[DEBUG] platform information: '+str(Platform.platform)

    @staticmethod
    def is_mac_10_8_plus():
        is_mac = Platform.is_mac()
        if is_mac:
            mac_version = Platform.platform['platformmacver'][0]
            mac_version_split = mac_version.split('.')
            is_mac_version_ok = (len(mac_version_split) >= 2 and int(mac_version_split[0]) == 10 and int(mac_version_split[1]) >= 8) or (len(mac_version_split) >= 1 and int(mac_version_split[0]) > 10)
            if GlobalParams.is_debug():
                print '[DEBUG] Mac version "'+mac_version+'" is 10.8 or later > '+str(is_mac_version_ok)
            if is_mac_version_ok:
                return True
        return False

    @staticmethod
    def is_mac():
        platform_system = Platform.platform['platformsystem']
        platform_mac_ver = Platform.platform['platformmacver'][0]
        is_system_mac = platform_system.lower() == 'darwin' and len(platform_mac_ver) > 0
        if GlobalParams.is_debug():
            print '[DEBUG] Checking if "'+ platform_system +'" with version "'+platform_mac_ver+'" is Mac OS > '+str(is_system_mac)
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
        if GlobalParams.is_debug():
            print '[DEBUG] Checking if "'+ platform_system +'" is Linux > '+str(is_system_linux)
        return is_system_linux

    @staticmethod
    def is_windows():
        platform_system = Platform.platform['platformsystem']
        is_system_windows = platform_system.lower() == 'windows'
        if GlobalParams.is_debug():
            print '[DEBUG] Checking if "'+ platform_system +'" is Windows > '+str(is_system_windows)
        return is_system_windows
