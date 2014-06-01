import subprocess


def notify_obj(notify_object):
    title = notify_object['title'] if 'title' in notify_object else None
    subtitle = notify_object['subtitle'] if 'subtitle' in notify_object else None
    message = notify_object['message'] if 'message' in notify_object else None
    sound = notify_object['sound'] if 'sound' in notify_object else None
    group = notify_object['group'] if 'group' in notify_object else None
    remove = notify_object['remove'] if 'remove' in notify_object else None
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

    # Mute output, since this normally only tells if there was an old notification being removed
    fh = open("NUL","w")
    subprocess.Popen('terminal-notifier {}'.format(' '.join(params)), shell=True, stderr=fh).wait()
    fh.close()
