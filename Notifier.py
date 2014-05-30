import argparse
import extra_functions
import configuration
from subprocess import Popen, PIPE, STDOUT
import signal


def parseConfigurationContents(contents):
    returnConfiguration = configuration.Configuration()
    lines = contents.split('\n')
    isCommands = False
    isConfig = False
    configData = None
    for line in lines:
        line = line.strip()
        if line is None or line[0:1] == '#':
            continue
        elif line.startswith('[COMMANDS]'):
            isCommands = True
            continue
        elif line.startswith('[/COMMANDS]'):
            isCommands = False
            continue
        elif isCommands:
            returnConfiguration.addCommand(line)
            continue
        elif line.startswith('[CONFIGURATION:'):
            isConfig = True
            configData = {'name': line[len('[CONFIGURATION:'):-1], 'graceTime': 500}
            continue
        elif line.startswith('[/CONFIGURATION:'):
            returnConfiguration.addConfig(configData)
            isConfig = False
            configData = None
            continue
        elif isConfig:
            if line.startswith('[PATTERN]'):
                configData['pattern'] = line[len('[PATTERN]'):]
            if line.startswith('[HISTORYPATTERN]'):
                configData['historyPattern'] = line[len('[HISTORYPATTERN]'):]
            elif line.startswith('[GRACETIME]'):
                gracetime = int(line[len('[GRACETIME]'):])
                configData['graceTime'] = gracetime
            elif line.startswith('[NOTIFICATION]'):
                line = line[len('[NOTIFICATION]'):]
                configData['notification'] = {}
                while len(line) > 0:
                    # Just do this by extracting what's in the brackets instead
                    if line.startswith('['):
                        notificationName = line[1:line.find(']')]
                        notificationNameLower = notificationName.lower()
                        line = line[len('['+notificationName+']'):]
                        value = line
                        nextParamStart = value.find('[')
                        if nextParamStart != -1:
                            value = value[0:nextParamStart]
                            line = line[nextParamStart:]
                        else:
                            line = ''
                        configData['notification'][notificationNameLower] = value

    return returnConfiguration

def parseConfigurationFile(configurationFile):
    if extra_functions.ExtraFileMethods.DoesFileExist(configurationFile):
        contents = extra_functions.ExtraFileMethods.GetFileContents(configurationFile)
        configuration = parseConfigurationContents(contents)
        return configuration
    else:
        exit(0)


def run(configuration, debug, mute):
    mergedCommands = ' ; '.join(configuration.commands)
    process = Popen(mergedCommands, stdout=PIPE, stderr=STDOUT, stdin=PIPE, shell=True)
    print mergedCommands
    accumulatedLines = []
    while True:
        nextline = process.stdout.readline().replace('\n', '')
        if not mute:
            print nextline
        if nextline == '' and process.poll() is not None:
            configuration.analyzeQuit(debug)
            break
        else:
            notificationSend = configuration.analyze(nextline, accumulatedLines, debug)
            if notificationSend:
                accumulatedLines = []
            else:
                accumulatedLines.append(nextline)
    pass

def userExited(signum, frame):
    print 'User terminated script'
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, userExited)
    parser = argparse.ArgumentParser(description='Run terminal commands in Mac OS X (10.8+) and get notifications on certain scenarios.')
    parser.add_argument('--config', help='Target configuration', required=True, type=str)
    parser.add_argument('--debug', help='Debug output', required=False, type=bool, default=False)
    parser.add_argument('--mute', help='Mute normal output', required=False, type=bool, default=False)
    args = vars(parser.parse_args())
    run(parseConfigurationFile(args['config']), args['debug'], args['mute'])
