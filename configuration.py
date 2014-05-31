import subprocess
import random
import re
import time
import LinuxNotifier
import OSXNotifier
import sys, os, platform


class Configuration:
    def __init__(self, debug):
        self.commands = []
        self.configs = []
        self.platform = {'osname': os.name, 'osuname': os.uname(), 'sysplatform': sys.platform, 'platformplatform': platform.platform(), 'platformsystem': platform.system(), 'platformrelease': platform.release(), 'platformversion': platform.version(), 'platformmacver': platform.mac_ver()}
        if debug:
            print '[DEBUG] platform information: '+str(self.platform)

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
            if self.isMac_10_8_plus(debug):
                OSXNotifier.notifyObj(notification)
            elif self.isLinux_with_notify_send(debug):
                if notificationSound is not None:
                    # Check if system supports aplay
                    aplaySupported = self.supportCommand(['aplay', '--version'], debug)
                    if debug:
                        if not aplaySupported:
                            print '[DEBUG] Playing sounds together with the notification is not supported in your system'
                        else:
                            self.runCommand(['aplay', notificationSound])
                            print '[DEBUG] Will try and play sound "'+notificationSound+'" through aplay'
                LinuxNotifier.notifyObj(notification)
            else:
                self.outputNotificationUnsupported()
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

    def outputNotificationUnsupported(self):
        print 'Your operating system is unsupported for outputting notifications at the moment'
        exit(0)

    def isMac_10_8_plus(self, debug):
        isMac = self.isMac(debug)
        if isMac:
            macVersion = self.platform['platformmacver'][0]
            macVersionSplit = macVersion.split('.')
            isMacVersionOk = (len(macVersionSplit) >= 2 and int(macVersionSplit[0]) == 10 and int(macVersionSplit[1]) >= 8) or (len(macVersionSplit) >= 1 and int(macVersionSplit[0]) > 10)
            if debug:
                print '[DEBUG] Mac version "'+macVersion+'" is 10.8 or later > '+str(isMacVersionOk)
            if isMacVersionOk:
                return True
        return False

    def isMac(self, debug):
        platform_system = self.platform['platformsystem']
        platform_mac_ver = self.platform['platformmacver'][0]
        isSystemMac = platform_system.lower() == 'darwin' and len(platform_mac_ver) > 0
        if debug:
            print '[DEBUG] Checking if "'+ platform_system +'" with version "'+platform_mac_ver+'" is Mac OS > '+str(isSystemMac)
        return isSystemMac

    def isLinux_with_notify_send(self, debug):
        isLinux = self.isLinux(debug)
        if isLinux:
            # Check if the command is actually there
            notifySendAvailable = self.supportCommand(['notify-send', '--version'], debug)
            if notifySendAvailable:
                return True
        return False

    def isLinux(self, debug):
        platform_system = self.platform['platformsystem']
        isSystemLinux = platform_system.lower() == 'linux'
        if debug:
            print '[DEBUG] Checking if "'+ platform_system +'" is Linux > '+str(isSystemLinux)
        return isSystemLinux

    def supportCommand(self, command, debug):
        supported = True
        commandName = command if isinstance(command, basestring) else command[0]
        try:
            self.runCommand(command)
            if debug:
                print '[DEBUG] Checking if '+commandName+' is available on system > True'
        except OSError:
            supported = False
            if debug:
                print '[DEBUG] Checking if '+commandName+' is available on system > False'
        return supported

    def runCommand(self, command):
        subprocess.call(command)
