import cherrypy
import logging
import functools

from blueberrypy.template_engine import get_template

from .auth_controller import AuthController


logger = logging.getLogger(__name__)


# decorator. apply to certain methods after 'exposed'
def render(template=None, page_id=None, menu=None):
    def dec(func):
        @functools.wraps(func)
        def wrapper(obj):
            '''
            obj is an object with context of func
            '''
            tmpl = get_template(template)
            return tmpl.render(webpage={
                               'content': func(obj),
                               'menu': (obj.menu
                                        if hasattr(obj, 'menu')
                                        else menu),
                               'current_page': page_id})
        return wrapper
    return dec


class Root:

    @cherrypy.expose
    # @render(template = 'gdg.org.ua_old.html', page_id = 'about')
    def index(self, **kwargs):
        from .api import get_all_gdg_places
        tmpl = get_template("gdg.org.ua_old.html")
        return tmpl.render(
            places=get_all_gdg_places(cherrypy.request.orm_session,
                                      filtered=True))

    @cherrypy.expose
    def admin(self, **kwargs):
        tmpl = get_template("admin/admin.html")
        return tmpl.render(p={})


Root.auth = AuthController()


# class API:
#    """It is an API router"""

#    @cherrypy.expose
#    def index(self, **kwargs):
#        return "API is privatei"

#    @cherrypy.expose
#    def default(self, *unparsed):
#        return self.index()

# class Participants:
#    """docstring for Participants"""

#    _KEY = 'fb6a10f172177dca7fb4de9d59c46a1e'

#    @cherrypy.expose
#    def index(self, **kwargs):
#        return "API is privates"

#    @cherrypy.expose
#    def default(self, **unparsed):
#        return self.index()

#    @cherrypy.expose
#    def add(self, *unparsed):
#        return "adding" # self.index()

#    @cherrypy.expose
#    def remove(self, *unparsed):
#        return 'removing' # self.index()

#    @cherrypy.expose
#    def edit(self, *unparsed):
#        return 'changing' # self.index()

#     @cherrypy.expose
#     def get(self, *unparsed):
#        return 'changing' # self.index()

#     @cherrypy.expose
#     class get:
#        """docstring for get"""

#        #def __init__(self, **arg):
#            #super(ClassName, self).__init__()
#            #self.arg = arg
#        #    pass

#        @cherrypy.expose
#        def index(self, **uid):
#            return 'get index' # self.index()

#        @cherrypy.expose
#        def x(self, **uid):
#            return 'get index' # self.index()

#        @cherrypy.expose
#        def default(self, **unparsed):
#            return 'changing' # self.index()

#     get = get()
#     get.default = default

# Root.api = API()
# Root.api.participants = Participants()
