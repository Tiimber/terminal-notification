from __future__ import print_function
from __future__ import unicode_literals
import argparse
import extra_functions
import configuration
from subprocess import Popen, PIPE, STDOUT
import signal
import glob
from time import sleep

try:
    import thread
except ImportError:
    pass

try:
    import _thread as thread
except ImportError:
    pass


process = None
need_restart = True

def parse_configuration_contents(contents):
    return_configuration = configuration.Configuration()
    lines = contents.split('\n')
    is_commands = False
    is_config = False
    config_data = None
    for line in lines:
        line = line.strip()
        if line is None or len(line) == 0 or line[0:1] == '#':
            continue
        elif line.startswith('[COMMANDS]'):
            is_commands = True
            continue
        elif line.startswith('[/COMMANDS]'):
            is_commands = False
            continue
        elif is_commands:
            return_configuration.add_command(line)
            continue
        elif line.startswith('[CONFIGURATION:'):
            is_config = True
            config_data = {'name': line[len('[CONFIGURATION:'):-1], 'graceTime': 500}
            continue
        elif line.startswith('[/CONFIGURATION:'):
            return_configuration.add_config(config_data)
            is_config = False
            config_data = None
            continue
        elif is_config:
            if line.startswith('[PATTERN]'):
                config_data['pattern'] = line[len('[PATTERN]'):]
            if line.startswith('[EXITCODE]'):
                config_data['exitcode'] = line[len('[EXITCODE]'):]
            if line.startswith('[HISTORYPATTERN]'):
                config_data['historyPattern'] = line[len('[HISTORYPATTERN]'):]
            elif line.startswith('[GRACETIME]'):
                gracetime = int(line[len('[GRACETIME]'):])
                config_data['graceTime'] = gracetime
            elif line.startswith('[TIMEOUT]'):
                timeout = int(line[len('[TIMEOUT]'):])
                config_data['timeout'] = timeout
            elif line.startswith('[RESTART]'):
                config_data['restart'] = True if line[len('[RESTART]'):].lower() == 'true' else False
            elif line.startswith('[NOTIFICATION]'):
                line = line[len('[NOTIFICATION]'):]
                config_data['notification'] = {}
                while len(line) > 0:
                    # Just do this by extracting what's in the brackets instead
                    if line.startswith('['):
                        notification_name = line[1:line.find(']')]
                        notification_name_lower = notification_name.lower()
                        line = line[len('['+notification_name+']'):]
                        value = line
                        next_param_start = value.find('[')
                        if next_param_start != -1:
                            value = value[0:next_param_start]
                            line = line[next_param_start:]
                        else:
                            line = ''
                        config_data['notification'][notification_name_lower] = value

    return return_configuration


def parse_configuration_file(configuration_file):
    glob.Debug.debug('[DEBUG] Checking if configuration file exists...')
    if extra_functions.FileHelper.does_file_exist(configuration_file):
        glob.Debug.debug('[DEBUG] Opening and parsing configuration file "'+configuration_file+'"...')
        contents = extra_functions.FileHelper.get_file_contents(configuration_file)
        parsed_configuration = parse_configuration_contents(contents)
        if len(parsed_configuration.commands) == 0:
            print(extra_functions.ColorOutput.get_colored('ERROR Configuration file don\'t have any commands to run...'))
            exit_notifier()
        return parsed_configuration
    else:
        print(extra_functions.ColorOutput.get_colored('ERROR: The specified file don\'t exist or couldn\'t be opened'))
        exit_notifier()


def run(parsed_configuration):
    parsed_configuration.analyze_startup()
    merged_commands = glob.Platform.get_command_line_merge_for_platform().join(parsed_configuration.commands)
    global process, need_restart
    while need_restart:
        need_restart = False
        process = Popen(merged_commands, stdout=PIPE, stderr=STDOUT, stdin=PIPE, shell=True)
        glob.Debug.debug('[DEBUG] Commands: '+merged_commands)
        accumulated_lines = []

        # Starting, make sure it's not considered as hanging already
        glob.Hang.update_last_time()
        # Start thread for checking for hanging scripts
        thread.start_new(function, (parsed_configuration,))

        while True:
            readline = process.stdout.readline()
            readline = readline.decode('utf-8')
            nextline = readline.replace('\n', '')

            # If we get output - it hasn't hung yet
            glob.Hang.update_last_time()
            glob.Hang.add_line(nextline)

            if not glob.GlobalParams.is_mute():
                print(extra_functions.ColorOutput.get_colored(nextline))
            process_poll = process.poll()
            if nextline == '' and process_poll is not None:
                glob.Debug.debug('[DEBUG] Process exit code: '+str(process_poll))
                if need_restart:
                    break
                else:
                    need_restart = parsed_configuration.analyze_quit(process_poll)
                    break
            else:
                notification_sent = parsed_configuration.analyze(nextline, accumulated_lines)
                if notification_sent:
                    accumulated_lines = []
                else:
                    accumulated_lines.append(nextline)

        if need_restart:
            print('Restart of process was requested!')


def kill_process():
    global process
    process.kill()

def restart_process():
    global process, need_restart
    need_restart = True
    process.kill()


def function(parsed_configuration):
    # Collect configuration times for hanging scripts
    hanging_times = parsed_configuration.get_hanging_times()
    if len(hanging_times) > 0:
        glob.Debug.debug('[DEBUG] Time thresholds for hanging configurations: '+str(hanging_times))

        last_elapsed = glob.Hang.get_elapsed()
        while True:
            elapsed = glob.Hang.get_elapsed()

            for threshold in hanging_times:
                if last_elapsed <= threshold <= elapsed:
                    restart = parsed_configuration.analyze_hanging_with_timeout(threshold, glob.Hang.get_lines())
                    if restart:
                        restart_process()

            sleep(0.05)
            last_elapsed = elapsed
    else:
        glob.Debug.debug('[DEBUG] No hanging detection needed since there were no configurations found for it')


def exit_notifier():
    extra_functions.FileHelper.remove_file("NUL")
    glob.GlobalParams.unset_color()
    exit(0)


def user_exited(signum, frame):
    print(extra_functions.ColorOutput.get_colored('User terminated script'))
    kill_process()
    exit_notifier()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, user_exited)
    parser = argparse.ArgumentParser(description='Run terminal commands in Mac OS X (10.8+) and get notifications on certain scenarios.')
    parser.add_argument('--config', help='Target configuration', required=True, type=str)
    parser.add_argument('--debug', help='Debug output', required=False, default=False, action='store_true')
    parser.add_argument('--mute', help='Mute normal output', required=False, default=False, action='store_true')
    parser.add_argument('--only-sound', help='Only play sounds, don\'t display notifications', required=False, default=False, action='store_true')
    parser.add_argument('--no-sound', help='Mute all sounds, can\'t be used if --only-sound is used', required=False, default=False, action='store_true')
    parser.add_argument('--growl', help='Use growl rather than system default', required=False, default=False, action='store_true')
    parser.add_argument('--color', help='Set color to use for all output', required=False, default=None, type=str)
    parser.add_argument('--mac-afplay', help='Override to use afplay (takes files instead of system sounds) to play sounds even if using Notification Center', required=False, default=False, action='store_true')
    parser.add_argument('--win-sounder', help='If you\'re on Windows and sounder.exe isn\'t automatically found, enter the full path to it here', required=False, type=str)
    args = vars(parser.parse_args())

    # Set debug and mute params
    glob.GlobalParams.set_debug(args['debug'])
    glob.GlobalParams.set_mute(args['mute'])
    glob.GlobalParams.set_growl(args['growl'])
    glob.GlobalParams.set_only_sound(args['only_sound'])
    glob.GlobalParams.set_no_sound(False if args['only_sound'] else args['no_sound'])

    # Set platform information
    glob.Platform.set_platform()

    # Colored output
    if 'color' in args:
        glob.GlobalParams.set_color(args['color'])

    # Output platform debug
    glob.Debug.debug('[DEBUG] platform information: '+str(glob.Platform.get_platform()))


    # If overriding sounder.exe position
    if 'win_sounder' in args and glob.Platform.is_windows():
        glob.GlobalParams.set_sounder(args['win_sounder'])

    # If overriding to use afplay on a mac
    if ('mac_afplay' in args and glob.Platform.is_mac()):
        glob.GlobalParams.set_afplay(args['mac_afplay'])

    run(parse_configuration_file(args['config']))
    exit_notifier()
