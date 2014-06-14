try:
    import gntp.notifier
except ImportError:
    pass


class GrowlNotifier():
    growl = None

    @staticmethod
    def register():
        if GrowlNotifier.growl is None:
            GrowlNotifier.growl = gntp.notifier.GrowlNotifier(
                applicationName='Terminal Notification',
                notifications=['Message'],
                defaultNotifications=['Message'],
            )
            growl_register = GrowlNotifier.growl.register()
            if not growl_register:
                GrowlNotifier.growl = None
        return GrowlNotifier.growl is not None

    @staticmethod
    def notify_obj(notify_object):
        if GrowlNotifier.growl is not None:
            title = str(notify_object['title']) if 'title' in notify_object else None
            subtitle = str(notify_object['subtitle']) if 'subtitle' in notify_object else None
            if title is not None and subtitle is not None:
                title = title + ' / ' + subtitle
            elif subtitle is not None:
                title = subtitle
            message = str(notify_object['message']) if 'message' in notify_object else None
            return GrowlNotifier.notify(title=title, message=message)
        else:
            return False

    @staticmethod
    def notify(title=None, message=None):
        notify_success = GrowlNotifier.growl.notify(
            noteType='Message',
            title=title,
            description=message,
            sticky=False,
            priority=1
        )
        return notify_success