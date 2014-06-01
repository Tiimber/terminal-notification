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
        if glob.GlobalParams.isDebug():
            print '[DEBUG] platform information: '+str(self.platform)

    def addConfig(self, config):
        self.configs.append(config)

    def addCommand(self, command):
        self.commands.append(command)

    def analyzeQuit(self):
        if glob.GlobalParams.isDebug():
            print '[DEBUG] Application is exiting, checking if there is a {QUIT} configuration...'
        self.analyzeSpecial('QUIT')

    def analyzeStartup(self):
        if glob.GlobalParams.isDebug():
            print '[DEBUG] Application is starting up, checking if there is a {STARTUP} configuration...'
        self.analyzeSpecial('STARTUP')

    def analyzeSpecial(self, action):
        actionLabel = '{' + action + '}'
        for config in self.configs:
            if config['name'] == actionLabel:
                if glob.GlobalParams.isDebug():
                    print '[DEBUG] '+actionLabel+' configuration found, will display notification if exists...'
                groups = []
                historyGroups = []
                notification = config['notification'] if 'notification' in config else None
                self.sendNotification(notification, groups, historyGroups, 0)

    def analyze(self, line, accumulated=None):
        line = self.stripColoring(line)
        if glob.GlobalParams.isDebug():
            print '[DEBUG] Check if line is triggering a notification: "'+line+'"'
        for config in self.configs:
            if config['name'] != '{QUIT}' and config['name'] != '{STARTUP}':
                pattern = config['pattern'] if 'pattern' in config else None
                historyPattern = config['historyPattern'] if 'historyPattern' in config else None
                if pattern is not None:
                    groups = re.findall(pattern, line)
                    historyGroups = []
                    if groups is not None and len(groups) > 0:
                        if historyPattern is not None and accumulated is not None:
                            accumulatedOneLine = self.stripColoring('[NL]'.join(accumulated))
                            historyGroups = re.findall(historyPattern, accumulatedOneLine)
                        if glob.GlobalParams.isDebug():
                            print '[DEBUG] Pattern is matching: "'+pattern+'"'
                        if 'lastTrigger' not in config or self.hasGraceTimePassed(config['lastTrigger'], config['graceTime']):
                            runCount = 0 if 'runCount' not in config else config['runCount']
                            config['runCount'] = runCount+1
                            notification = config['notification'] if 'notification' in config else None
                            self.sendNotification(notification, [groups] if isinstance(groups, basestring) else groups[0], [historyGroups] if isinstance(historyGroups, basestring) else (historyGroups[0] if len(historyGroups) > 0 else []), runCount)
                            config['lastTrigger'] = int(time.time() * 1000)
                            return True
                        else:
                            if glob.GlobalParams.isDebug():
                                print '[DEBUG] Gracetime haven\'t passed yet - will not triggering notification'
        return False

    def sendNotification(self, notification, groups, historyGroups, runCount):
        groups = [groups] if isinstance(groups, basestring) else groups
        historyGroups = [historyGroups] if isinstance(historyGroups, basestring) else historyGroups
        if notification is not None:
            notificationSound = None
            originalNotificationSound = None
            if glob.GlobalParams.isDebug():
                print '[DEBUG] Notification found: '
            for key in notification:
                if glob.GlobalParams.isDebug():
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
                if glob.GlobalParams.isDebug():
                    print '[DEBUG] value='+value
                notification[key] = value
            if glob.GlobalParams.isDebug():
                print '[DEBUG] Pushing notification: '+str(notification)
            notification['sound'] = notificationSound
            if self.isMac_10_8_plus():
                osx_notifier.notifyObj(notification)
            elif self.isLinux_with_notify_send():
                if notificationSound is not None:
                    # Check if system supports aplay
                    aplaySupported = self.supportCommand(['aplay', '--version'])
                    if glob.GlobalParams.isDebug():
                        if not aplaySupported:
                            print '[DEBUG] Playing sounds together with the notification is not supported in your system'
                        else:
                            self.runCommandAsync(['aplay', notificationSound])
                            print '[DEBUG] Will try and play sound "'+notificationSound+'" through aplay'
                linux_notifier.notifyObj(notification)
            elif self.isWindows():
                # TODO - Windows GNTP or notification through power shell?!
                self.outputNotificationUnsupported()
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

    def isMac_10_8_plus(self):
        isMac = self.isMac()
        if isMac:
            macVersion = self.platform['platformmacver'][0]
            macVersionSplit = macVersion.split('.')
            isMacVersionOk = (len(macVersionSplit) >= 2 and int(macVersionSplit[0]) == 10 and int(macVersionSplit[1]) >= 8) or (len(macVersionSplit) >= 1 and int(macVersionSplit[0]) > 10)
            if glob.GlobalParams.isDebug():
                print '[DEBUG] Mac version "'+macVersion+'" is 10.8 or later > '+str(isMacVersionOk)
            if isMacVersionOk:
                return True
        return False

    def isMac(self):
        platform_system = self.platform['platformsystem']
        platform_mac_ver = self.platform['platformmacver'][0]
        isSystemMac = platform_system.lower() == 'darwin' and len(platform_mac_ver) > 0
        if glob.GlobalParams.isDebug():
            print '[DEBUG] Checking if "'+ platform_system +'" with version "'+platform_mac_ver+'" is Mac OS > '+str(isSystemMac)
        return isSystemMac

    def isLinux_with_notify_send(self):
        isLinux = self.isLinux()
        if isLinux:
            # Check if the command is actually there
            notifySendAvailable = self.supportCommand(['notify-send', '--version'])
            if notifySendAvailable:
                return True
        return False

    def isLinux(self):
        platform_system = self.platform['platformsystem']
        isSystemLinux = platform_system.lower() == 'linux'
        if glob.GlobalParams.isDebug():
            print '[DEBUG] Checking if "'+ platform_system +'" is Linux > '+str(isSystemLinux)
        return isSystemLinux

    def isWindows(self):
        platform_system = self.platform['platformsystem']
        isSystemWindows = platform_system.lower() == 'windows'
        if glob.GlobalParams.isDebug():
            print '[DEBUG] Checking if "'+ platform_system +'" is Windows > '+str(isSystemWindows)
        return isSystemWindows

    def supportCommand(self, command):
        supported = True
        commandName = command if isinstance(command, basestring) else command[0]
        try:
            self.runCommand(command)
            if glob.GlobalParams.isDebug():
                print '[DEBUG] Checking if '+commandName+' is available on system > True'
        except OSError:
            supported = False
            if glob.GlobalParams.isDebug():
                print '[DEBUG] Checking if '+commandName+' is available on system > False'
        return supported

    def runCommand(self, command):
        subprocess.call(command)

    def runCommandAsync(self, command):
        subprocess.Popen(command)
