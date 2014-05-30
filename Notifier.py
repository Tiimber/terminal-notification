import argparse
import extra_functions
import configuration
from subprocess import Popen, PIPE, STDOUT


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
            configData = {'name': line[len('[CONFIGURATION:'):-1]}
            continue
        elif line.startswith('[/CONFIGURATION:'):
            returnConfiguration.addConfig(configData)
            isConfig = False
            configData = None
            continue
        elif isConfig:
            if line.startswith('[PATTERN]'):
                configData['pattern'] = line[len('[PATTERN]'):]
            elif line.startswith('[NOTIFICATION]'):
                line = line[len('[NOTIFICATION]'):]
                configData['notification'] = {}
                while len(line) > 0:
                    # Just do this by extracting what's in the brackets instead
                    if line.startswith('[TITLE]'):
                        line = line[len('[TITLE]'):]
                        title = line
                        nextParamStart = title.find('[')
                        if nextParamStart != -1:
                            title = title[0:nextParamStart]
                            line = line[nextParamStart:]
                        else:
                            line = ''
                        configData['notification']['title'] = title
                    elif line.startswith('[SUBTITLE]'):
                        line = line[len('[SUBTITLE]'):]
                        subtitle = line
                        nextParamStart = subtitle.find('[')
                        if nextParamStart != -1:
                            subtitle = subtitle[0:nextParamStart]
                            line = line[nextParamStart:]
                        else:
                            line = ''
                        configData['notification']['subtitle'] = subtitle
                    elif line.startswith('[MESSAGE]'):
                        line = line[len('[MESSAGE]'):]
                        message = line
                        nextParamStart = message.find('[')
                        if nextParamStart != -1:
                            message = message[0:nextParamStart]
                            line = line[nextParamStart:]
                        else:
                            line = ''
                        configData['notification']['message'] = message
                    elif line.startswith('[SOUND]'):
                        line = line[len('[SOUND]'):]
                        sound = line
                        nextParamStart = sound.find('[')
                        if nextParamStart != -1:
                            sound = sound[0:nextParamStart]
                            line = line[nextParamStart:]
                        else:
                            line = ''
                        configData['notification']['sound'] = sound
                    elif line.startswith('[GROUP]'):
                        line = line[len('[GROUP]'):]
                        group = line
                        nextParamStart = group.find('[')
                        if nextParamStart != -1:
                            group = group[0:nextParamStart]
                            line = line[nextParamStart:]
                        else:
                            line = ''
                        configData['notification']['group'] = group

    return returnConfiguration

def parseConfigurationFile(configurationFile):
    if extra_functions.ExtraFileMethods.DoesFileExist(configurationFile):
        contents = extra_functions.ExtraFileMethods.GetFileContents(configurationFile)
        configuration = parseConfigurationContents(contents)
        return configuration
    else:
        exit(0)


def run(configuration):
    mergedCommands = ' ; '.join(configuration.commands)
    process = Popen(mergedCommands, stdout=PIPE, stderr=STDOUT, stdin=PIPE, shell=True)
    print mergedCommands
    accumulatedLines = []
    while True:
        nextline = process.stdout.readline()
        print nextline
        if nextline == '' and process.poll() is not None:
            configuration.analyzeQuit()
            break
        else:
            notificationSend = configuration.analyze(nextline, accumulatedLines)
            if notificationSend:
                accumulatedLines = []
            else:
                accumulatedLines.append(nextline)
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run terminal commands in Mac OS X (10.8+) and get notifications on certain scenarios.')
    parser.add_argument('--config', help='Target configuration', required=True, type=str)
    args = vars(parser.parse_args())
    run(parseConfigurationFile(args['config']))
