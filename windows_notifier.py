import glob
import os


def notify_obj(notify_object):
    title = notify_object['title'] if 'title' in notify_object else None
    subtitle = notify_object['subtitle'] if 'subtitle' in notify_object else None
    if title is not None and subtitle is not None:
        title = title + ' / ' + subtitle
    elif subtitle is not None:
        title = subtitle
    message = notify_object['message'] if 'message' in notify_object else None
    time = notify_object['time'] if 'time' in notify_object else None
    notify(title=title, message=message, time=time)


def notify(title=None, message=None, time=None):
    params = []
    if title is not None:
        t = '/p "{!r}"'.format(title)
        params.append(t)
    if message is not None:
        m = '/m "{!r}"'.format(message)
        params.append(m)
    if time is not None:
        t = '/d '+int(time/1000)
        params.append(t)
    else:
        t = '/d 3'
        params.append(t)

    os.system('START /MIN /B notifu {}'.format(' '.join(params)))
