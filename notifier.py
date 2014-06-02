import argparse
import extra_functions
import configuration
from subprocess import Popen, PIPE, STDOUT
import signal
import glob


def parse_configuration_contents(contents):
    return_configuration = configuration.Configuration()
    lines = contents.split('\n')
    is_commands = False
    is_config = False
    config_data = None
    for line in lines:
        line = line.strip()
        if line is None or line[0:1] == '#':
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
            if line.startswith('[HISTORYPATTERN]'):
                config_data['historyPattern'] = line[len('[HISTORYPATTERN]'):]
            elif line.startswith('[GRACETIME]'):
                gracetime = int(line[len('[GRACETIME]'):])
                config_data['graceTime'] = gracetime
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
    if glob.GlobalParams.is_debug():
        print '[DEBUG] Checking if configuration file exists...'
    if extra_functions.FileHelper.does_file_exist(configuration_file):
        if glob.GlobalParams.is_debug():
            print '[DEBUG] Opening and parsing configuration file "'+configuration_file+'"...'
        contents = extra_functions.FileHelper.get_file_contents(configuration_file)
        parsed_configuration = parse_configuration_contents(contents)
        if len(parsed_configuration.commands) == 0:
            print 'ERROR Configuration file don\'t have any commands to run...'
            exit(0)
        return parsed_configuration
    else:
        print 'ERROR: The specified file don\'t exist or couldn\'t be opened'
        exit(0)


def run(parsed_configuration):
    parsed_configuration.analyze_startup()
    merged_commands = glob.Platform.getCommandLineMergeForPlatform().join(parsed_configuration.commands)
    process = Popen(merged_commands, stdout=PIPE, stderr=STDOUT, stdin=PIPE, shell=True)
    if glob.GlobalParams.is_debug():
        print '[DEBUG] Commands: '+merged_commands
    accumulated_lines = []
    while True:
        nextline = process.stdout.readline().replace('\n', '')
        if not glob.GlobalParams.is_mute():
            print nextline
        if nextline == '' and process.poll() is not None:
            parsed_configuration.analyze_quit()
            break
        else:
            notification_sent = parsed_configuration.analyze(nextline, accumulated_lines)
            if notification_sent:
                accumulated_lines = []
            else:
                accumulated_lines.append(nextline)
    pass


def user_exited(signum, frame):
    print 'User terminated script'
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, user_exited)
    parser = argparse.ArgumentParser(description='Run terminal commands in Mac OS X (10.8+) and get notifications on certain scenarios.')
    parser.add_argument('--config', help='Target configuration', required=True, type=str)
    parser.add_argument('--debug', help='Debug output', required=False, default=False, action='store_true')
    parser.add_argument('--mute', help='Mute normal output', required=False, default=False, action='store_true')
    parser.add_argument('--only-sound', help='Only play sounds, don\'t display notifications', required=False, default=False, action='store_true')
    parser.add_argument('--no-sound', help='Mute all sounds, can\'t be used if --only-sound is used', required=False, default=False, action='store_true')
    parser.add_argument('--growl', help='Use growl rather than system default', required=False, default=False, action='store_true')
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

    # If overriding sounder.exe position
    if 'win_sounder' in args and glob.Platform.is_windows():
        glob.GlobalParams.set_sounder(args['win_sounder'])

    # If overriding to use afplay on a mac
    if ('mac_afplay' in args and glob.Platform.is_mac()):
        glob.GlobalParams.set_afplay(args['mac_afplay'])

    run(parse_configuration_file(args['config']))
