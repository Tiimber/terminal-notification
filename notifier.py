from __future__ import print_function
from __future__ import unicode_literals
import argparse
import extra_functions
import configuration
from subprocess import Popen, PIPE, STDOUT
import signal
import glob
from time import sleep
from random import randint
import zipfile

try:
    import cStringIO as io
except ImportError:
    try:
        import StringIO as io
    except ImportError:
        import io

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
    from urllib.request import HTTPError
    is_python_3 = True
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
    from urllib2 import HTTPError
    is_python_3 = False

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
runtime_tmp_id = 'tmp_' + str(extra_functions.TimeHelper.get_time()) + '_' + str(randint(100000, 999999))


def override_settings(line):
    if glob.GlobalParams.is_no_override_settings():
        glob.Debug.debug('[DEBUG] Configuration file was denied to override setting: ' + str(line))
    else:
        glob.Debug.debug('[DEBUG] Requested setting from configuration file: ' + str(line))
        is_not = False
        if line.startswith('!'):
            is_not = True
            line = line[1:].strip()

        set_bool_val = not is_not
        if line == '--debug':
            glob.GlobalParams.set_debug(set_bool_val)
        elif line == '--mute':
            glob.GlobalParams.set_mute(set_bool_val)
        elif line == '--growl':
            glob.GlobalParams.set_growl(set_bool_val)
        elif line == '--only_sound':
            glob.GlobalParams.set_only_sound(set_bool_val)
        elif line == '--no_sound':
            glob.GlobalParams.set_no_sound(set_bool_val)
        elif line == '--mac_afplay':
            glob.GlobalParams.set_afplay(set_bool_val)
        elif line.startswith('--color'):
            if is_not or '=' not in line:
                glob.GlobalParams.unset_color()
            else:
                color = line[line.find('=') + 1:]
                glob.GlobalParams.set_color(color)


def parse_configuration_contents(contents):
    return_configuration = configuration.Configuration()
    lines = contents.split('\n')
    is_settings = False
    is_commands = False
    is_config = False
    config_data = None
    for line in lines:
        line = line.strip()
        if line is None or len(line) == 0 or line[0:1] == '#':
            continue
        elif line.startswith('[SETTINGS]'):
            is_settings = True
            continue
        elif line.startswith('[/SETTINGS]'):
            is_settings = False
            continue
        elif is_settings:
            override_settings(line)
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
                        line = line[len('[' + notification_name + ']'):]
                        value = line

                        # Resolve sounds packaged in zip to the temporary folder
                        if notification_name_lower == 'sound':
                            if 'zip:' in value:
                                value = value.replace('zip:', runtime_tmp_id + '/')

                        next_param_start = value.find('[')
                        if next_param_start != -1:
                            value = value[0:next_param_start]
                            line = line[next_param_start:]
                        else:
                            line = ''
                        config_data['notification'][notification_name_lower] = value

    return return_configuration


def parse_configuration_file(configuration_file):
    if configuration_file.endswith('.zip'):
        glob.Debug.debug('[DEBUG] Zip package detected as config, will try and extract it temporarily...')
        if not configuration_file.startswith('http') and not configuration_file.startswith('file://'):
            configuration_file = 'file://' + configuration_file

        glob.Debug.debug('[DEBUG] Opening and parsing configuration file in zip "' + configuration_file + '"...')
        try:
            decided_config = False
            # Read zip-file
            zip = None
            if is_python_3:
                remotezip = urlopen(configuration_file)
                remotezip_read = remotezip.read()
                zipinmemory = io.BytesIO(remotezip_read)

                zip = zipfile.ZipFile(zipinmemory, 'r')
            else:
                remotezip = urlopen(configuration_file)
                remotezip_read = remotezip.read()
                zipinmemory = io.StringIO(remotezip_read)

                zip = zipfile.ZipFile(zipinmemory, 'r')

            # Create tmp directory with these files
            glob.Debug.debug('[DEBUG] Creating temporary folder for zip-contents: "' + runtime_tmp_id + '"')
            extra_functions.FileHelper.create_directory(runtime_tmp_id)

            for fn in zip.namelist():
                binary_contents = zip.read(fn)
                extra_functions.FileHelper.write_bytes_to_file(runtime_tmp_id + '/' + fn, binary_contents)

                if fn.endswith('platform-route.txt'):
                    configuration_file = get_configuration_in_route(
                        extra_functions.FileHelper.get_file_contents(runtime_tmp_id + '/' + fn))
                    decided_config = True
                elif not decided_config and fn.replace('.txt', '.zip') in configuration_file:
                    configuration_file = runtime_tmp_id + '/' + fn

            return parse_configuration_file(configuration_file)
        except HTTPError:
            print(extra_functions.ColorOutput.get_colored('ERROR Configuration file couldn\'t load...'))
            exit_notifier()

    glob.Debug.debug('[DEBUG] Checking if configuration file "' + configuration_file + '" exists...')
    if extra_functions.FileHelper.does_file_exist(configuration_file):
        glob.Debug.debug('[DEBUG] Opening and parsing configuration file "' + configuration_file + '"...')
        contents = extra_functions.FileHelper.get_file_contents(configuration_file)
        parsed_configuration = parse_configuration_contents(contents)
        if len(parsed_configuration.commands) == 0:
            print(
                extra_functions.ColorOutput.get_colored('ERROR Configuration file don\'t have any commands to run...'))
            exit_notifier()
        return parsed_configuration
    else:
        print(extra_functions.ColorOutput.get_colored('ERROR: The specified file don\'t exist or couldn\'t be opened'))
        exit_notifier()


def get_configuration_in_route(contents):
    configuration_file_for_system = ''
    lines = str(contents).split('\n')
    for line in lines:
        if line.find(':') != -1:
            config_platform = line[0:line.find(':')]
            config_file = line[len(config_platform) + 1:]
            glob.Debug.debug(
                '[DEBUG] Configuration file for platform "' + config_platform + '" is "' + config_file + '"')
            if (config_platform == 'mac' and glob.Platform.is_mac()) or (
                config_platform == 'lin' and glob.Platform.is_linux()) or (
                config_platform == 'win' and glob.Platform.is_windows()):
                glob.Debug.debug('[DEBUG] Will use configuration file "' + config_file + '"')
                configuration_file_for_system = config_file.replace('zip:', runtime_tmp_id + '/')
                break
    return configuration_file_for_system


def run(parsed_configuration):
    parsed_configuration.analyze_startup()
    merged_commands = glob.Platform.get_command_line_merge_for_platform().join(parsed_configuration.commands)
    global process, need_restart
    while need_restart:
        need_restart = False
        process = Popen(merged_commands, stdout=PIPE, stderr=STDOUT, stdin=PIPE, shell=True)
        glob.Debug.debug('[DEBUG] Commands: ' + merged_commands)
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
                glob.Debug.debug('[DEBUG] Process exit code: ' + str(process_poll))
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
        else:
            if extra_functions.FileHelper.does_file_exist(runtime_tmp_id):
                # Sleep a little while before exiting - to allow possible playing of quit-sound
                sleep(2)


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
        glob.Debug.debug('[DEBUG] Time thresholds for hanging configurations: ' + str(hanging_times))

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
    # Remove temporary stderror and stdoutput file
    extra_functions.FileHelper.remove_file("NUL")

    # Remove tmp directory with with zip contents
    glob.Debug.debug('[DEBUG] Removing temporary folder for zip-contents: "' + runtime_tmp_id + '"')
    extra_functions.FileHelper.remove_directory(runtime_tmp_id)

    glob.GlobalParams.unset_color()
    exit(0)


def user_exited(signum, frame):
    print(extra_functions.ColorOutput.get_colored('User terminated script'))
    kill_process()
    exit_notifier()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, user_exited)
    parser = argparse.ArgumentParser(
        description='Run terminal commands in Mac OS X (10.8+) and get notifications on certain scenarios.')
    parser.add_argument('--config', help='Target configuration', required=True, type=str)
    parser.add_argument('--debug', help='Debug output', required=False, default=False, action='store_true')
    parser.add_argument('--mute', help='Mute normal output', required=False, default=False, action='store_true')
    parser.add_argument('--only-sound', help='Only play sounds, don\'t display notifications', required=False,
                        default=False, action='store_true')
    parser.add_argument('--no-sound', help='Mute all sounds, can\'t be used if --only-sound is used', required=False,
                        default=False, action='store_true')
    parser.add_argument('--growl', help='Use growl rather than system default', required=False, default=False,
                        action='store_true')
    parser.add_argument('--color', help='Set color to use for all output', required=False, default=None, type=str)
    parser.add_argument('--mac-afplay',
                        help='Override to use afplay (takes files instead of system sounds) to play sounds even if using Notification Center',
                        required=False, default=False, action='store_true')
    parser.add_argument('--no-override-settings', help='Do not allow any bundled settings', required=False,
                        default=False, action='store_true')
    args = vars(parser.parse_args())

    # Set global params
    glob.GlobalParams.set_no_override_settings(args['no_override_settings'])
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
    glob.Debug.debug('[DEBUG] platform information: ' + str(glob.Platform.get_platform()))

    # If overriding to use afplay on a mac
    if ('mac_afplay' in args and glob.Platform.is_mac()):
        glob.GlobalParams.set_afplay(args['mac_afplay'])

    run(parse_configuration_file(args['config']))
    exit_notifier()
