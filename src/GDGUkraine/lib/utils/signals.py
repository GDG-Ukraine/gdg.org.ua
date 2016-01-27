import cherrypy as cp
from cherrypy.process.wspbus import ChannelFailures


def pub(channel, *args, **kwargs):
    try:
        return cp.engine.publish(channel, *args, **kwargs).pop()
    except ChannelFailures as cf:
        # Unwrap exception, which happened in channel
        raise cf.get_instances()[0] from cf
