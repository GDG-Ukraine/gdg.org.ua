import cherrypy
from cherrypy import HTTPError, HTTPRedirect
from blueberrypy.template_engine import get_template
import social
from datetime import date, datetime
import json
from blueberrypy.util import from_collection, to_collection

import logging


logger = logging.getLogger(__name__)

# decorator. apply to certain methods after 'exposed'
def render(template = None, page_id = None, ):
    def dec(func):
        @functools.wraps(func)
        def wrapper(obj):
            '''
            obj is an object with context of func
            '''
            tmpl = get_template(template)
            return tmpl.render(webpage = { 'content': func(obj), 'menu': obj.menu if hasattr(obj, 'menu') else menu, 'current_page': page_id })
        return wrapper
    return dec

class Root:

    @cherrypy.expose
    #@render(template = 'gdg.org.ua_old.html', page_id = 'about')
    def index(self, **kwargs):
        from .api import get_all_gdg_places
        #tmpl = get_template("index.html")
        tmpl = get_template("gdg.org.ua_old.html")
        return tmpl.render(places=get_all_gdg_places(cherrypy.request.orm_session, filtered = True))

    @cherrypy.expose
    def admin(self, **kwargs):
        tmpl = get_template("admin/admin.html")
        return tmpl.render(p = {})

    def auth(self):
        import social
        raise HTTPRedirect('http://google.com')

    @cherrypy.expose
    def test(self):
        if not cherrypy.session.get('test_counter'):
            cherrypy.session['test_counter'] = 0
        cherrypy.session['test_counter'] += 1
        logger.debug('>>>>>>global test start')
        logger.debug('session' in dir(cherrypy))
        logger.debug(cherrypy.session.get('test_counter'))
        logger.debug('<<<<<<global test stop')
        return 'global test'

class OAuth2:
    """docstring for OAuth2"""
    def __init__(self, arg = None):
        super(OAuth2, self).__init__()
        self.arg = arg
    
    @cherrypy.expose
    def google(self):
        req = cherrypy.request
        forward_url = req.headers.get("Referer", "/")
        raise HTTPRedirect('http://google.com/{0}'.format(forward_url))

    index = google

Root.auth = OAuth2()

    #@cherrypy.expose
    #def default(self, *unparsed):
    #    print('lol')
    #    return self.index()

class Events:

    #def create(self, **kwargs):
    #    req = cherrypy.request
    #    orm_session = req.orm_session
    #    event = from_collection(req.json, Event())
    #    orm_session.add(event)
    #    orm_session.commit()
    #    return to_collection(event, sort_keys=True)

    def show(self, id, **kwargs):
        id = int(id)
        from .api import find_event_by_id, find_host_gdg_by_event
        event = find_event_by_id(cherrypy.request.orm_session, id)
        if event:
            tmpl = get_template("event.html")
            return tmpl.render(event=event)
        raise HTTPError(404)

    def register(self, id, **kwargs):
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        from .api import find_event_by_id, find_host_gdg_by_event, get_all_events
        event = find_event_by_id(orm_session, id)
        events_list = None
        if event:
            if (event.max_regs is None or event.max_regs > len(event.participants)) and event.date > date.today() and (event.closereg is None or event.closereg > date.today()):
                tmpl = get_template("register.html")
            else:
                tmpl = get_template("regclosed.html")
                events_list = get_all_events(orm_session, 5, hide_closed = True)
            return tmpl.render(event=event, events=events_list, user=None)
        #return tmpl.render(event=event, user=cherrypy.session.get('user'))
        raise HTTPError(404)

    def list_all(self, **kwargs):
        from .api import get_all_events
        events = get_all_events(cherrypy.request.orm_session)
        if events:
            tmpl = get_template("events.html")
            return tmpl.render(events=events)
        raise HTTPError(404)

    def update(self, id, **kwargs):
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        from .api import find_event_by_id
        event = find_event_by_id(orm_session, id)
        if event:
            orm_session.commit()
            return event
        raise HTTPError(404)

    def delete(self, id, **kwargs):
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        from .api import delete_event_by_id
        if not delete_event_by_id(orm_session, id):
            raise HTTPError(404)
        else:
            orm_session.commit()
    
    def test(self, **kwargs):
        req = cherrypy.request
        orm_session = req.orm_session
        #logger.debug(req)
        #logger.debug(dir(req))
        #logger.debug(dir(req.app))
        logger.debug('>>>>>>REST test start')
        #cherrypy.tools.sessions.callable()
        logger.debug('session' in dir(cherrypy))
        logger.debug(cherrypy.session)
        logger.debug(cherrypy.session.get('test_counter'))
        logger.debug('<<<<<<REST test stop')
        return 'counter is {0}'.format(cherrypy.session.get('test_counter'))

events = cherrypy.dispatch.RoutesDispatcher()
events.mapper.explicit = False
events.connect("test", "/test", Events, action="test",
                        conditions={"method":["GET"]})
#events.connect("add", "/", Events, action="create",
#                        conditions={"method":["POST"]})
events.connect("list", "", Events, action="list_all",
                        conditions={"method":["GET"]})
events.connect("get", "/{id}", Events, action="show",
                        conditions={"method":["GET"]})
events.connect("edit", "/{id}", Events, action="update",
                        conditions={"method":["PUT"]})
events.connect("remove", "/{id}", Events, action="delete",
                        conditions={"method":["DELETE"]})
events.connect("register", "/{id}/register", Events, action="register",
                        conditions={"method":["GET"]})

#class API:
#    """It is an API router"""
#
#    @cherrypy.expose
#    def index(self, **kwargs):
#        return "API is privatei"
#
#    @cherrypy.expose
#    def default(self, *unparsed):
#        return self.index()
#        
#class Participants:
#    """docstring for Participants"""
#    
#    _KEY = 'fb6a10f172177dca7fb4de9d59c46a1e'
#    
#    @cherrypy.expose
#    def index(self, **kwargs):
#        return "API is privates"
#
#    @cherrypy.expose
#    def default(self, **unparsed):
#        return self.index()
#
#    @cherrypy.expose
#    def add(self, *unparsed):
#        return "adding" # self.index()
#
#    @cherrypy.expose
#    def remove(self, *unparsed):
#        return 'removing' # self.index()
#        
#    @cherrypy.expose
#    def edit(self, *unparsed):
#        return 'changing' # self.index()
# 
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
