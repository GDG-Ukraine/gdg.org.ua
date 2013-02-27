import cherrypy
from blueberrypy.template_engine import get_template

class Root:

    @cherrypy.expose
    def index(self, **kwargs):
        tmpl = get_template("index.html")
        return tmpl.render()

    @cherrypy.expose
    def admin(self, **kwargs):
        tmpl = get_template("participants.html")
        return tmpl.render()

    @cherrypy.expose
    def default(self, *unparsed):
        return self.index()

class API:
    """It is an API router"""

    @cherrypy.expose
    def index(self, **kwargs):
        return "API is privatei"

    @cherrypy.expose
    def default(self, *unparsed):
        return self.index()
        
class Participants:
    """docstring for Participants"""
    
    _API_KEY = 'fb6a10f172177dca7fb4de9d59c46a1e'
    
    @cherrypy.expose
    def index(self, **kwargs):
        return "API is privates"

    @cherrypy.expose
    def default(self, **unparsed):
        return self.index()

    @cherrypy.expose
    def add(self, *unparsed):
        return "adding" # self.index()

    @cherrypy.expose
    def remove(self, *unparsed):
        return 'removing' # self.index()
        
    @cherrypy.expose
    def edit(self, *unparsed):
        return 'changing' # self.index()
 
    #@cherrypy.expose
    #def get(self, *unparsed):
    #    return 'changing' # self.index()

    #@cherrypy.expose
    #class get:
    #    """docstring for get"""

    #    #def __init__(self, **arg):
    #        #super(ClassName, self).__init__()
    #        #self.arg = arg
    #    #    pass
    #     
    #    @cherrypy.expose
    #    def index(self, **uid):
    #        return 'get index' # self.index()

    #    @cherrypy.expose
    #    def x(self, **uid):
    #        return 'get index' # self.index()

    #    @cherrypy.expose
    #    def default(self, **unparsed):
    #        return 'changing' # self.index()

    #get = get()
    #get.default = default

#Root.api = API()
#Root.api.participants = Participants()
