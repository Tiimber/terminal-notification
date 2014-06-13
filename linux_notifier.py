import subprocess


def notify_obj(notify_object):
    title = str(notify_object['title']) if 'title' in notify_object else None
    subtitle = str(notify_object['subtitle']) if 'subtitle' in notify_object else None
    if title is not None and subtitle is not None:
        title = title + ' / ' + subtitle
    elif subtitle is not None:
        title = subtitle
    message = str(notify_object['message']) if 'message' in notify_object else None
    time = str(notify_object['time']) if 'time' in notify_object else None
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

    fh = open("NUL", "w")
    subprocess.Popen('notify-send {}'.format(' '.join(params)), shell=True, stderr=fh).wait()
    fh.close()
