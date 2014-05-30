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

    def analyzeQuit(self, debug=False):
        if debug:
            print '[DEBUG] Application is exiting, checking if there is a {QUIT} configuration...'
        for config in self.configs:
            if config['name'] == '{QUIT}':
                if debug:
                    print '[DEBUG] {QUIT} configuration found, will display notification if exists...'
                groups = []
                notification = config['notification'] if 'notification' in config else None
                self.sendNotification(notification, groups, debug)

    def analyze(self, line, accumulated=None, debug=False):
        if debug:
            print '[DEBUG] Check if line is triggering a notification: "'+line+'"'
        for config in self.configs:
            if config['name'] != '{QUIT}':
                pattern = config['pattern'] if 'pattern' in config else None
                if pattern is not None:
                    groups = re.findall(pattern, line)
                    if groups is not None and len(groups) > 0:
                        if debug:
                            print '[DEBUG] Pattern is matching: "'+pattern+'"'
                        notification = config['notification'] if 'notification' in config else None
                        self.sendNotification(notification, [groups] if isinstance(groups, basestring) else groups[0], debug)
                        return True
        return False

    def sendNotification(self, notification, groups, debug=False):
        groups = [groups] if isinstance(groups, basestring) else groups
        if notification is not None:
            if debug:
                print '[DEBUG] Notification found: '
            for key in notification:
                if debug:
                    print '[DEBUG] key='+key
                value = notification[key]
                matches = re.findall('\$([0-9]+)', value)
                if matches is not None:
                    for match in matches:
                        number = int(match)
                        if len(groups) > number-1:
                            replaceValue = groups[number-1]
                            value = value.replace('$'+str(number), replaceValue)
                if debug:
                    print '[DEBUG] value='+value
                notification[key] = value
        if debug:
            print '[DEBUG] Pushing notification: '+str(notification)
        OSXNotifier.notifyObj(notification)
