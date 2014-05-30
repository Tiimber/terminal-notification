import random
import re
import time
import OSXNotifier


class Configuration:
    def __init__(self):
        self.commands = []
        self.configs = []

    def addConfig(self, config):
        self.configs.append(config)

    def addCommand(self, command):
        self.commands.append(command)

    def analyzeQuit(self, debug=False):
        if debug:
            print '[DEBUG] Application is exiting, checking if there is a {QUIT} configuration...'
        for config in self.configs:
            if config['name'] == '{QUIT}':
                if debug:
                    print '[DEBUG] {QUIT} configuration found, will display notification if exists...'
                groups = []
                historyGroups = []
                notification = config['notification'] if 'notification' in config else None
                self.sendNotification(notification, groups, historyGroups, debug)

    def analyze(self, line, accumulated=None, debug=False):
        line = self.stripColoring(line)
        if debug:
            print '[DEBUG] Check if line is triggering a notification: "'+line+'"'
        for config in self.configs:
            if config['name'] != '{QUIT}':
                pattern = config['pattern'] if 'pattern' in config else None
                historyPattern = config['historyPattern'] if 'historyPattern' in config else None
                if pattern is not None:
                    groups = re.findall(pattern, line)
                    historyGroups = []
                    if groups is not None and len(groups) > 0:
                        if historyPattern is not None and accumulated is not None:
                            accumulatedOneLine = self.stripColoring('[NL]'.join(accumulated))
                            historyGroups = re.findall(historyPattern, accumulatedOneLine)
                        if debug:
                            print '[DEBUG] Pattern is matching: "'+pattern+'"'
                        if 'lastTrigger' not in config or self.hasGraceTimePassed(config['lastTrigger'], config['graceTime']):
                            runCount = 0 if 'runCount' not in config else config['runCount']
                            config['runCount'] = runCount+1
                            notification = config['notification'] if 'notification' in config else None
                            self.sendNotification(notification, [groups] if isinstance(groups, basestring) else groups[0], [historyGroups] if isinstance(historyGroups, basestring) else (historyGroups[0] if len(historyGroups) > 0 else []), runCount, debug)
                            config['lastTrigger'] = int(time.time() * 1000)
                            return True
                        else:
                            if debug:
                                print '[DEBUG] Gracetime haven\'t passed yet - will not triggering notification'
        return False

    def sendNotification(self, notification, groups, historyGroups, runCount, debug=False):
        groups = [groups] if isinstance(groups, basestring) else groups
        historyGroups = [historyGroups] if isinstance(historyGroups, basestring) else historyGroups
        if notification is not None:
            notificationSound = None
            originalNotificationSound = None
            if debug:
                print '[DEBUG] Notification found: '
            for key in notification:
                if debug:
                    print '[DEBUG] key='+key
                value = notification[key]
                if key == 'sound':
                    originalNotificationSound = value
                    notificationSound = self.getNotificationSound(value, runCount)
                matches = re.findall('\$([0-9]+)', value)
                if matches is not None:
                    for match in matches:
                        number = int(match)
                        if len(groups) > number-1:
                            replaceValue = groups[number-1]
                            value = value.replace('$'+str(number), replaceValue)
                historyMatches = re.findall('\$H([0-9]+)', value)
                if historyMatches is not None:
                    for match in historyMatches:
                        number = int(match)
                        if len(historyGroups) > number-1:
                            replaceValue = historyGroups[number-1]
                            value = value.replace('$H'+str(number), replaceValue)
                if debug:
                    print '[DEBUG] value='+value
                notification[key] = value
            if debug:
                print '[DEBUG] Pushing notification: '+str(notification)
            notification['sound'] = notificationSound
            OSXNotifier.notifyObj(notification)
            notification['sound'] = originalNotificationSound


    def stripColoring(self, line):
        matches = re.findall('\[[0-9]+\w', line)
        if matches is not None and isinstance(matches, basestring):
            matches = [matches]
        if matches is not None and len(matches) > 0:
            for match in matches:
                line = line.replace(match, '')
        return line

    def hasGraceTimePassed(self, lastTrigger, graceTime):
        currentTime = int(time.time() * 1000)
        return currentTime - graceTime >= lastTrigger

    def getNotificationSound(self, sound, runCount):
        if sound is not None:
            if sound.startswith('{cycle}'):
                soundList = sound[len('{cycle}'):].split(',')
                if runCount >= len(soundList):
                    runCount = runCount % len(soundList)
                sound = soundList[runCount]
            elif sound.startswith('{random}'):
                soundList = sound[len('{random}'):].split(',')
                sound = soundList[random.randint(0, len(soundList)-1)]
        return sound