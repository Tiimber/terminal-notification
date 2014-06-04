import random
import re
import extra_functions
import glob
import growl_notifier
import linux_notifier
import notifier
import osx_notifier

# GNTP might not be installed
import windows_notifier

try:
    import gntp.notifier
except ImportError:
    pass


class Configuration:
    def __init__(self):
        self.commands = []
        self.configs = []

    def add_config(self, config):
        self.configs.append(config)

    def add_command(self, command):
        self.commands.append(command)

    def analyze_quit(self, exitcode):
        if glob.GlobalParams.is_debug():
            print extra_functions.ColorOutput.get_colored('[DEBUG] Application is exiting, checking if there is a {QUIT} configuration...')
        return self.analyze_special('QUIT', exitcode)

    def analyze_startup(self):
        if glob.GlobalParams.is_debug():
            print extra_functions.ColorOutput.get_colored('[DEBUG] Application is starting up, checking if there is a {STARTUP} configuration...')
        # Register growl if it's requested
        if glob.GlobalParams.prefer_growl():
            Configuration.init_growl()
        self.analyze_special('STARTUP')

    def analyze_special(self, action, exitcode=None):
        action_label = '{' + action + '}'
        for config in self.configs:
            if config['name'] == action_label:
                if glob.GlobalParams.is_debug():
                    print extra_functions.ColorOutput.get_colored('[DEBUG] '+action_label+' configuration found, will display notification if exists...')
                groups = []
                history_groups = []
                notification = config['notification'] if 'notification' in config else None
                on_exitcode_val = config['exitcode'] if 'exitcode' in config else None
                if_exitcode = False if on_exitcode_val is not None and on_exitcode_val.startswith('{not}') else True
                on_exitcode = 0 if on_exitcode_val is None else (int(on_exitcode_val) if not '}' in on_exitcode_val else int(on_exitcode_val[on_exitcode_val.find('}')+1:]))
                exitcode_match = on_exitcode_val is None or (on_exitcode == exitcode) == if_exitcode

                if on_exitcode_val is not None and glob.GlobalParams.is_debug():
                    print extra_functions.ColorOutput.get_colored('[DEBUG] Trigger notification if ' + ('not ' if not if_exitcode else ' ') + str(exitcode) + ' == ' + str(on_exitcode))
                    if exitcode_match:
                        print extra_functions.ColorOutput.get_colored('[DEBUG] Exit code condition matched, will trigger this notification')

                if exitcode_match:
                    self.send_notification(notification, groups, history_groups, 0)
                    return 'restart' in config and config['restart']
        return False

    def get_hanging_times(self):
        hanging_times = []
        for config in self.configs:
            if config['name'] == '{HANGING}':
                hanging_times.append(config['timeout'])
                if glob.GlobalParams.is_debug():
                    print extra_functions.ColorOutput.get_colored('[DEBUG] HANGING configuration found, time: '+str(config['timeout']))
        return hanging_times

    def analyze_hanging_with_timeout(self, threshold, last_lines):
        if glob.GlobalParams.is_debug():
            print extra_functions.ColorOutput.get_colored('[DEBUG] Scanning for HANGING configurations that should trigger after '+str(threshold)+'ms...')
        for config in self.configs:
            if config['name'] == '{HANGING}' and threshold == config['timeout']:
                if glob.GlobalParams.is_debug():
                    print extra_functions.ColorOutput.get_colored('[DEBUG] Found configuration: '+str(config))
                notify_hanging = True
                if 'pattern' in config:
                    notify_hanging = False
                    # Check if pattern is applicable on the specified line
                    pattern = config['pattern']
                    line_number_to_analyze = 0
                    is_if = True
                    if pattern.startswith('{'):
                        condition_part = pattern[:pattern.find('}')+1]
                        pattern = pattern[len(condition_part):]
                        condition_part = condition_part[1:len(condition_part)-1]
                        is_if = not condition_part.startswith('ifnot')
                        condition_part = condition_part.replace('ifnot', '').replace('if', '').replace(':', '')
                        try:
                            line_number_to_analyze = int(condition_part)
                        except ValueError:
                            line_number_to_analyze = 0

                    line_to_analyze = None if len(last_lines) <= line_number_to_analyze else last_lines[line_number_to_analyze]

                    if glob.GlobalParams.is_debug():
                        print extra_functions.ColorOutput.get_colored('[DEBUG] Hanging ' + ('if' if is_if else 'if not') + ' "'+pattern+'" in line: '+str(line_number_to_analyze) + ' "'+str(line_to_analyze)+'"')

                    matches = None if line_to_analyze is None else re.findall(pattern, line_to_analyze)
                    if (is_if and (matches is not None and len(matches) > 0)) or (not is_if and (matches is None or len(matches) == 0)):
                        notify_hanging = True
                    else:
                        if glob.GlobalParams.is_debug():
                            print extra_functions.ColorOutput.get_colored('[DEBUG] HANGING configuration did not meet the pattern, will not display notification...')

                if notify_hanging:
                    if glob.GlobalParams.is_debug():
                        print extra_functions.ColorOutput.get_colored('[DEBUG] HANGING configuration with passed timeout found, will display notification if exists...')
                    groups = []
                    history_groups = []
                    notification = config['notification'] if 'notification' in config else None
                    self.send_notification(notification, groups, history_groups, 0)
                    # Ask the thread to kill the running process and restart it
                    return 'restart' in config and config['restart']
        return False

    def analyze(self, line, accumulated=None):
        line = extra_functions.CommandHelper.strip_coloring(line)
        if glob.GlobalParams.is_debug():
            print extra_functions.ColorOutput.get_colored('[DEBUG] Check if line is triggering a notification: "'+line+'"')
        for config in self.configs:
            if not config['name'].startswith('{') and not config['name'].endswith('}'):
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
                            print extra_functions.ColorOutput.get_colored('[DEBUG] Pattern is matching: "'+pattern+'"')
                        if 'lastTrigger' not in config or extra_functions.TimeHelper.has_time_passed(config['lastTrigger'], config['graceTime']):
                            run_count = 0 if 'runCount' not in config else config['runCount']
                            config['runCount'] = run_count+1
                            notification = config['notification'] if 'notification' in config else None
                            self.send_notification(notification, [groups] if isinstance(groups, basestring) else groups[0], [history_groups] if isinstance(history_groups, basestring) else (history_groups[0] if len(history_groups) > 0 else []), run_count)
                            config['lastTrigger'] = extra_functions.TimeHelper.get_time()
                            return True
                        else:
                            if glob.GlobalParams.is_debug():
                                print extra_functions.ColorOutput.get_colored('[DEBUG] Gracetime haven\'t passed yet - will not triggering notification')
        return False

    def send_notification(self, notification, groups, history_groups, run_count):
        groups = [groups] if isinstance(groups, basestring) else groups
        history_groups = [history_groups] if isinstance(history_groups, basestring) else history_groups
        if notification is not None:
            notification_sound = None
            original_notification_sound = None
            if glob.GlobalParams.is_debug():
                print extra_functions.ColorOutput.get_colored('[DEBUG] Notification found: ')
            for key in notification:
                if glob.GlobalParams.is_debug():
                    print extra_functions.ColorOutput.get_colored('[DEBUG] key='+key)
                value = notification[key]
                if key == 'sound':
                    original_notification_sound = value
                    notification_sound = Configuration.get_notification_sound(value, run_count)
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
                    print extra_functions.ColorOutput.get_colored('[DEBUG] value='+value)
                notification[key] = value
            if glob.GlobalParams.is_debug():
                print extra_functions.ColorOutput.get_colored('[DEBUG] Pushing notification: '+str(notification))

            # No sound option?
            notification['sound'] = notification_sound
            if glob.GlobalParams.is_no_sound():
                notification['sound'] = '{none}'
                if glob.GlobalParams.is_debug():
                    print extra_functions.ColorOutput.get_colored('[DEBUG] No sound will be played, as --no-sound have been set')

            # Growl ONLY if requested
            will_use_growl = False
            if glob.GlobalParams.prefer_growl():
                if not glob.GlobalParams.is_only_sound():
                    will_use_growl = growl_notifier.GrowlNotifier.notify_obj(notification)
                else:
                    will_use_growl = True
                    if glob.GlobalParams.is_debug():
                        print extra_functions.ColorOutput.get_colored('[DEBUG] No notification will be displayed, as --only-sound have been set')
                if not will_use_growl:
                    print extra_functions.ColorOutput.get_colored('ERROR: You requested to use Growl for notification, but Growl failed to give notification. Will try to use standard service instead')

            # Play sound in external sound player
            if notification_sound is not None:
                Configuration.play_sound(notification['sound'])

            # If not requested growl or if failed - run default for system
            if not will_use_growl:
                if not glob.GlobalParams.is_only_sound():
                    if glob.Platform.is_mac_10_8_plus():
                        # If overridden to play sound externally
                        if glob.GlobalParams.use_afplay():
                            notification['sound'] = '{none}'
                        osx_notifier.notify_obj(notification)
                    elif glob.Platform.is_linux_with_notify_send():
                        linux_notifier.notify_obj(notification)
                    elif glob.Platform.is_windows():
                        windows_notifier.notify_obj(notification)
                    else:
                        Configuration.output_notification_unsupported()
                else:
                    if glob.GlobalParams.is_debug():
                        print extra_functions.ColorOutput.get_colored('[DEBUG] No notification will be displayed, as --only-sound have been set')
            notification['sound'] = original_notification_sound

    @staticmethod
    def output_notification_unsupported():
        print extra_functions.ColorOutput.get_colored('Your operating system is unsupported for outputting notifications at the moment')
        notifier.exit_notifier()

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

    @staticmethod
    def module_exists(module_name):
        try:
            __import__(module_name)
        except ImportError:
            return False
        else:
            return True

    @staticmethod
    def init_growl():
        will_use_growl = Configuration.module_exists('gntp')
        if will_use_growl:
            if glob.GlobalParams.is_debug():
                print extra_functions.ColorOutput.get_colored('[DEBUG] User have requested to use Growl for notifications, will try and register application')
            register_success = growl_notifier.GrowlNotifier.register()
            if not register_success:
                print extra_functions.ColorOutput.get_colored('ERROR: You requested to use Growl for notification, but Growl failed to instantiate. Will try to use standard service instead')
                glob.GlobalParams.set_growl(False)
            elif glob.GlobalParams.is_debug():
                print extra_functions.ColorOutput.get_colored('[DEBUG] User have requested to use Growl for notifications, will try and register application')
        else:
            print extra_functions.ColorOutput.get_colored('ERROR: Growl isn\'t available on your system. Will try to use standard service instead')
            glob.GlobalParams.set_growl(False)

    @staticmethod
    def play_sound(notification_sound):
        if notification_sound != '{none}':
            if glob.Platform.is_linux():
                # Check if system supports aplay
                aplay_supported = extra_functions.CommandHelper.support_command(['aplay', '--version'])
                if not aplay_supported:
                    if glob.GlobalParams.is_debug():
                        print extra_functions.ColorOutput.get_colored('[DEBUG] Playing sounds together with the notification is not supported in your system')
                else:
                    extra_functions.CommandHelper.run_command_async(['aplay', notification_sound])
                    if glob.GlobalParams.is_debug():
                        print extra_functions.ColorOutput.get_colored('[DEBUG] Will try and play sound "'+notification_sound+'" through aplay')
            elif glob.Platform.is_windows():
                # Check if system supports sounder
                sounder_supported = extra_functions.CommandHelper.support_command([glob.GlobalParams.get_sounder()])
                if not sounder_supported:
                    if glob.GlobalParams.is_debug():
                        print extra_functions.ColorOutput.get_colored('[DEBUG] Playing sounds together with the notification is not supported in your system')
                else:
                    extra_functions.CommandHelper.run_command_async([glob.GlobalParams.get_sounder(), notification_sound])
                    if glob.GlobalParams.is_debug():
                        print extra_functions.ColorOutput.get_colored('[DEBUG] Will try and play sound "'+notification_sound+'" through sounder')
            elif glob.Platform.is_mac():
                if glob.GlobalParams.prefer_growl() or glob.GlobalParams.use_afplay():
                    if glob.GlobalParams.is_debug():
                        # Check if system supports afplay
                        afplay_supported = extra_functions.CommandHelper.support_command(['afplay', '--help'])
                        if not afplay_supported:
                            if glob.GlobalParams.is_debug():
                                print extra_functions.ColorOutput.get_colored('[DEBUG] Playing sounds together with the notification is not supported in your system')
                        else:
                            extra_functions.CommandHelper.run_command_async(['afplay', notification_sound])
                            if glob.GlobalParams.is_debug():
                                print extra_functions.ColorOutput.get_colored('[DEBUG] Will try and play sound "'+notification_sound+'" through afplay')
                elif glob.GlobalParams.is_debug():
                    print extra_functions.ColorOutput.get_colored('[DEBUG] Mac will play sound through the standard Sound Effects')
