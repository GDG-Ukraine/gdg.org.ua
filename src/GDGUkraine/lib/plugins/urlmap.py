import cherrypy
from cherrypy.process.plugins import SimplePlugin

from ..utils.url import build_url_map


class UrlMapPlugin(SimplePlugin):
    """UrlForPlugin is a CherryPy plugin, that builds a URL Map for url builder
    """
    def __init__(self, *args, **kwargs):
        super(UrlMapPlugin, self).__init__(*args, **kwargs)

    def start(self):
        try:
            build_url_map(force=True)
            self.bus.log('URL map has been built. '
                         'url_for should now work correctly.')
        except:
            self.bus.log('Building of URL map failed!')
            self.bus.log(traceback=True)


def register():
    # Register the plugin in CherryPy:
    if not hasattr(cherrypy.engine, 'url_for'):
        cherrypy.engine.url_for = UrlMapPlugin(cherrypy.engine)
# Enable UrlMap plugin as follows:
# global:
#   engine.url_for.on: true
