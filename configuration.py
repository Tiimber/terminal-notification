import random
import re
import extra_functions
import glob
import linux_notifier
import osx_notifier


class Configuration:
    def __init__(self):
        self.commands = []
        self.configs = []

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
        line = extra_functions.CommandHelper.strip_coloring(line)
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
                            accumulated_one_line = extra_functions.CommandHelper.strip_coloring('[NL]'.join(accumulated))
                            history_groups = re.findall(history_pattern, accumulated_one_line)
                        if glob.GlobalParams.is_debug():
                            print '[DEBUG] Pattern is matching: "'+pattern+'"'
                        if 'lastTrigger' not in config or extra_functions.TimeHelper.has_time_passed(config['lastTrigger'], config['graceTime']):
                            run_count = 0 if 'runCount' not in config else config['runCount']
                            config['runCount'] = run_count+1
                            notification = config['notification'] if 'notification' in config else None
                            self.send_notification(notification, [groups] if isinstance(groups, basestring) else groups[0], [history_groups] if isinstance(history_groups, basestring) else (history_groups[0] if len(history_groups) > 0 else []), run_count)
                            config['lastTrigger'] = extra_functions.TimeHelper.get_time()
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
                    notification_sound = Configuration.get_notification_sound(value, runCount)
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
            if glob.Platform.is_mac_10_8_plus():
                osx_notifier.notify_obj(notification)
            elif glob.Platform.is_linux_with_notify_send():
                if notification_sound is not None:
                    # Check if system supports aplay
                    aplay_supported = extra_functions.CommandHelper.support_command(['aplay', '--version'])
                    if glob.GlobalParams.is_debug():
                        if not aplay_supported:
                            print '[DEBUG] Playing sounds together with the notification is not supported in your system'
                        else:
                            extra_functions.CommandHelper.run_command_async(['aplay', notification_sound])
                            print '[DEBUG] Will try and play sound "'+notification_sound+'" through aplay'
                linux_notifier.notify_obj(notification)
            elif glob.Platform.is_windows():
                # TODO - Windows GNTP or notification through power shell?!
                Configuration.output_notification_unsupported()
            else:
                Configuration.output_notification_unsupported()
            notification['sound'] = original_notification_sound

    @staticmethod
    def output_notification_unsupported():
        print 'Your operating system is unsupported for outputting notifications at the moment'
        exit(0)

    @staticmethod
    def get_notification_sound(sound, run_count):
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
