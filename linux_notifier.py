import subprocess


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
        t = '{!r}'.format(title)
        params.append(t)
    if message is not None:
        m = '{!r}'.format(message)
        params.append(m)
    if time is not None:
        t = '-t {!r}'.format(time)
        params.append(t)

    subprocess.Popen('notify-send {}'.format(' '.join(params)), shell=True).wait()