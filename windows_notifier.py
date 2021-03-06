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
        t = '/p "{!r}"'.format(title)
        params.append(t)
    if message is not None:
        m = '/m "{!r}"'.format(message)
        params.append(m)
    if time is not None:
        time_seconds = int(int(time) / 1000)
        t = '/d '+str(time_seconds)
        params.append(t)
    else:
        t = '/d 3'
        params.append(t)
    # Never play sound in notifu
    params.append('/q')

    # Mute output, since this normally only tells if there was an old notification being removed
    fh = open("NUL","w")
    subprocess.Popen('START /MIN /B notifu {}'.format(' '.join(params)), shell=True, stderr=fh).wait()
    fh.close()
