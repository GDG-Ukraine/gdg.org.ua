import cherrypy
from .urlmap import UrlMapPlugin


def register_plugins():
    # Register the plugin in CherryPy:
    if not hasattr(cherrypy.engine, 'url_for'):
        cherrypy.engine.url_for = UrlMapPlugin(cherrypy.engine)


# Enable UrlMap plugin as follows:
# global:
#   engine.url_for.on: true
