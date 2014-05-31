import os

def notifyObj(notifyObject):
    title = notifyObject['title'] if 'title' in notifyObject else None
    subtitle = notifyObject['subtitle'] if 'subtitle' in notifyObject else None
    if title is not None and subtitle is not None:
        title = title + '/' + subtitle
    elif subtitle is not None:
        title = subtitle
    message = notifyObject['message'] if 'message' in notifyObject else None
    time = notifyObject['time'] if 'time' in notifyObject else None
    notify(title=title, message=message, time=time)


def notify(title=None, message=None, time=None):
    params = []
    if title is not None:
        t = '{!r}'.format(title)
        params.append(t)
    if message is not None:
        m = '{!r}'.format(message)
        params.append(m)
    if time is not None:
        t = '-t {!r}'.format(time)
        params.append(t)

    os.system('notify-send {}'.format(' '.join(params)))
