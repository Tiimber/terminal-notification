import re
import OSXNotifier


class Configuration:
    def __init__(self):
        self.commands = []
        self.configs = []

    def addConfig(self, config):
        self.configs.append(config)

    def addCommand(self, command):
        self.commands.append(command)

    def analyzeQuit(self):
        for config in self.configs:
            if config['name'] == '{QUIT}':
                groups = []
                notification = config['notification'] if 'notification' in config else None
                self.sendNotification(notification, groups)

    def analyze(self, line, accumulated=None):
        for config in self.configs:
            if config['name'] != '{QUIT}':
                pattern = config['pattern'] if 'pattern' in config else None
                if pattern is not None:
                    groups = re.findall(pattern, line)
                    if groups is not None and len(groups) > 0:
                        notification = config['notification'] if 'notification' in config else None
                        self.sendNotification(notification, [groups] if isinstance(groups, basestring) else groups[0])
                        return True
        return False

    def sendNotification(self, notification, groups):
        groups = [groups] if isinstance(groups, basestring) else groups
        if notification is not None:
            for key in notification:
                value = notification[key]
                matches = re.findall('\$([0-9]+)', value)
                if matches is not None:
                    for match in matches:
                        number = int(match)
                        if len(groups) > number-1:
                            replaceValue = groups[number-1]
                            value = value.replace('$'+str(number), replaceValue)
                notification[key] = value
        OSXNotifier.notifyObj(notification)
