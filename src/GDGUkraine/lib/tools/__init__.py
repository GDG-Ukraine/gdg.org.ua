import cherrypy
from .authorize import AuthorizeTool


def register_tools():
    if not hasattr(cherrypy.tools, 'authorize'):
        cherrypy.tools.authorize = AuthorizeTool()
