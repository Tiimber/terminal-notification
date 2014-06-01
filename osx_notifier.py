import os

def notifyObj(notifyObject):
    title = notifyObject['title'] if 'title' in notifyObject else None
    subtitle = notifyObject['subtitle'] if 'subtitle' in notifyObject else None
    message = notifyObject['message'] if 'message' in notifyObject else None
    sound = notifyObject['sound'] if 'sound' in notifyObject else None
    group = notifyObject['group'] if 'group' in notifyObject else None
    remove = notifyObject['remove'] if 'remove' in notifyObject else None
    notify(title=title, subtitle=subtitle, message=message, sound=sound, group=group, remove=remove)


def notify(title=None, subtitle=None, message=None, sound=None, group=None, remove=None):
    params = []
    if title is not None:
        t = '-title {!r}'.format(title)
        params.append(t)
    if subtitle is not None:
        s = '-subtitle {!r}'.format(subtitle)
        params.append(s)
    if message is not None:
        m = '-message {!r}'.format(message)
        params.append(m)
    if sound is not None:
        so = '-sound {!r}'.format(sound)
        params.append(so)
    if group is not None:
        g = '-group {!r}'.format(group)
        params.append(g)
    if remove is not None:
        r = '-remove {!r}'.format(remove)
        params.append(r)

    os.system('terminal-notifier {}'.format(' '.join(params)))
