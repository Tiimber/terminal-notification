import subprocess
import random
import re
import time
import glob
import linux_notifier
import osx_notifier
import sys, os, platform


class Configuration:
    def __init__(self):
        self.commands = []
        self.configs = []
        os_uname = None
        try:
            os_uname = os.uname()
        except AttributeError:
            os_uname = None
        self.platform = {'osname': os.name, 'osuname': os_uname, 'sysplatform': sys.platform, 'platformplatform': platform.platform(), 'platformsystem': platform.system(), 'platformrelease': platform.release(), 'platformversion': platform.version(), 'platformmacver': platform.mac_ver()}
        if glob.GlobalParams.is_debug():
            print '[DEBUG] platform information: '+str(self.platform)

    def add_config(self, config):
        self.configs.append(config)

    def add_command(self, command):
        self.commands.append(command)

    def analyze_quit(self):
        if glob.GlobalParams.is_debug():
            print '[DEBUG] Application is exiting, checking if there is a {QUIT} configuration...'
        self.analyze_special('QUIT')

    def analyze_startup(self):
        if glob.GlobalParams.is_debug():
            print '[DEBUG] Application is starting up, checking if there is a {STARTUP} configuration...'
        self.analyze_special('STARTUP')

    def analyze_special(self, action):
        action_label = '{' + action + '}'
        for config in self.configs:
            if config['name'] == action_label:
                if glob.GlobalParams.is_debug():
                    print '[DEBUG] '+action_label+' configuration found, will display notification if exists...'
                groups = []
                history_groups = []
                notification = config['notification'] if 'notification' in config else None
                self.send_notification(notification, groups, history_groups, 0)

    def analyze(self, line, accumulated=None):
        line = self.strip_coloring(line)
        if glob.GlobalParams.is_debug():
            print '[DEBUG] Check if line is triggering a notification: "'+line+'"'
        for config in self.configs:
            if config['name'] != '{QUIT}' and config['name'] != '{STARTUP}':
                pattern = config['pattern'] if 'pattern' in config else None
                history_pattern = config['historyPattern'] if 'historyPattern' in config else None
                if pattern is not None:
                    groups = re.findall(pattern, line)
                    history_groups = []
                    if groups is not None and len(groups) > 0:
                        if history_pattern is not None and accumulated is not None:
                            accumulated_one_line = self.strip_coloring('[NL]'.join(accumulated))
                            history_groups = re.findall(history_pattern, accumulated_one_line)
                        if glob.GlobalParams.is_debug():
                            print '[DEBUG] Pattern is matching: "'+pattern+'"'
                        if 'lastTrigger' not in config or self.has_gracetime_passed(config['lastTrigger'], config['graceTime']):
                            run_count = 0 if 'runCount' not in config else config['runCount']
                            config['runCount'] = run_count+1
                            notification = config['notification'] if 'notification' in config else None
                            self.send_notification(notification, [groups] if isinstance(groups, basestring) else groups[0], [history_groups] if isinstance(history_groups, basestring) else (history_groups[0] if len(history_groups) > 0 else []), run_count)
                            config['lastTrigger'] = int(time.time() * 1000)
                            return True
                        else:
                            if glob.GlobalParams.is_debug():
                                print '[DEBUG] Gracetime haven\'t passed yet - will not triggering notification'
        return False

    def send_notification(self, notification, groups, history_groups, runCount):
        groups = [groups] if isinstance(groups, basestring) else groups
        history_groups = [history_groups] if isinstance(history_groups, basestring) else history_groups
        if notification is not None:
            notification_sound = None
            original_notification_sound = None
            if glob.GlobalParams.is_debug():
                print '[DEBUG] Notification found: '
            for key in notification:
                if glob.GlobalParams.is_debug():
                    print '[DEBUG] key='+key
                value = notification[key]
                if key == 'sound':
                    original_notification_sound = value
                    notification_sound = self.get_notification_sound(value, runCount)
                matches = re.findall('\$([0-9]+)', value)
                if matches is not None:
                    for match in matches:
                        number = int(match)
                        if len(groups) > number-1:
                            replace_value = groups[number-1]
                            value = value.replace('$'+str(number), replace_value)
                history_matches = re.findall('\$H([0-9]+)', value)
                if history_matches is not None:
                    for match in history_matches:
                        number = int(match)
                        if len(history_groups) > number-1:
                            replace_value = history_groups[number-1]
                            value = value.replace('$H'+str(number), replace_value)
                if glob.GlobalParams.is_debug():
                    print '[DEBUG] value='+value
                notification[key] = value
            if glob.GlobalParams.is_debug():
                print '[DEBUG] Pushing notification: '+str(notification)
            notification['sound'] = notification_sound
            if self.is_mac_10_8_plus():
                osx_notifier.notify_obj(notification)
            elif self.is_linux_with_notify_send():
                if notification_sound is not None:
                    # Check if system supports aplay
                    aplay_supported = self.support_command(['aplay', '--version'])
                    if glob.GlobalParams.is_debug():
                        if not aplay_supported:
                            print '[DEBUG] Playing sounds together with the notification is not supported in your system'
                        else:
                            self.run_command_async(['aplay', notification_sound])
                            print '[DEBUG] Will try and play sound "'+notification_sound+'" through aplay'
                linux_notifier.notify_obj(notification)
            elif self.is_windows():
                # TODO - Windows GNTP or notification through power shell?!
                self.output_notification_unsupported()
            else:
                self.output_notification_unsupported()
            notification['sound'] = original_notification_sound


    def strip_coloring(self, line):
        matches = re.findall('\[[0-9]+\w', line)
        if matches is not None and isinstance(matches, basestring):
            matches = [matches]
        if matches is not None and len(matches) > 0:
            for match in matches:
                line = line.replace(match, '')
        return line

    def has_gracetime_passed(self, last_trigger, gracetime):
        current_time = int(time.time() * 1000)
        return current_time - gracetime >= last_trigger

    def get_notification_sound(self, sound, run_count):
        if sound is not None:
            if sound.startswith('{cycle}'):
                sound_list = sound[len('{cycle}'):].split(',')
                if run_count >= len(sound_list):
                    run_count = run_count % len(sound_list)
                sound = sound_list[run_count]
            elif sound.startswith('{random}'):
                sound_list = sound[len('{random}'):].split(',')
                sound = sound_list[random.randint(0, len(sound_list)-1)]
        return sound

    def output_notification_unsupported(self):
        print 'Your operating system is unsupported for outputting notifications at the moment'
        exit(0)

    def is_mac_10_8_plus(self):
        is_mac = self.is_mac()
        if is_mac:
            mac_version = self.platform['platformmacver'][0]
            mac_version_split = mac_version.split('.')
            is_mac_version_ok = (len(mac_version_split) >= 2 and int(mac_version_split[0]) == 10 and int(mac_version_split[1]) >= 8) or (len(mac_version_split) >= 1 and int(mac_version_split[0]) > 10)
            if glob.GlobalParams.is_debug():
                print '[DEBUG] Mac version "'+mac_version+'" is 10.8 or later > '+str(is_mac_version_ok)
            if is_mac_version_ok:
                return True
        return False

    def is_mac(self):
        platform_system = self.platform['platformsystem']
        platform_mac_ver = self.platform['platformmacver'][0]
        is_system_mac = platform_system.lower() == 'darwin' and len(platform_mac_ver) > 0
        if glob.GlobalParams.is_debug():
            print '[DEBUG] Checking if "'+ platform_system +'" with version "'+platform_mac_ver+'" is Mac OS > '+str(is_system_mac)
        return is_system_mac

    def is_linux_with_notify_send(self):
        is_linux = self.is_linux()
        if is_linux:
            # Check if the command is actually there
            notify_send_available = self.support_command(['notify-send', '--version'])
            if notify_send_available:
                return True
        return False

    def is_linux(self):
        platform_system = self.platform['platformsystem']
        is_system_linux = platform_system.lower() == 'linux'
        if glob.GlobalParams.is_debug():
            print '[DEBUG] Checking if "'+ platform_system +'" is Linux > '+str(is_system_linux)
        return is_system_linux

    def is_windows(self):
        platform_system = self.platform['platformsystem']
        is_system_windows = platform_system.lower() == 'windows'
        if glob.GlobalParams.is_debug():
            print '[DEBUG] Checking if "'+ platform_system +'" is Windows > '+str(is_system_windows)
        return is_system_windows

    def support_command(self, command):
        supported = True
        commandName = command if isinstance(command, basestring) else command[0]
        try:
            self.run_command(command)
            if glob.GlobalParams.is_debug():
                print '[DEBUG] Checking if '+commandName+' is available on system > True'
        except OSError:
            supported = False
            if glob.GlobalParams.is_debug():
                print '[DEBUG] Checking if '+commandName+' is available on system > False'
        return supported

    def run_command(self, command):
        subprocess.call(command)

    def run_command_async(self, command):
        subprocess.Popen(command)
