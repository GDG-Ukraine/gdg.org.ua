import cherrypy
import logging

from cherrypy import HTTPError, HTTPRedirect

from datetime import date, datetime

from blueberrypy.template_engine import get_template
from blueberrypy.util import from_collection, to_collection


logger = logging.getLogger(__name__)


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
        u = None
        i = None
        if event:
            if kwargs.get('code'):
                from .api import find_invitation_by_code, find_user_by_email
                i = find_invitation_by_code(orm_session, kwargs['code'])
                if i is None or i.used or i.event != event:
                    raise HTTPError(403, "Invalid invite code.")
                if i.email is not None:
                    u = find_user_by_email(orm_session, i.email)
            if kwargs.get('code') or (event.max_regs is None or event.max_regs > len(event.participants)) and event.date > date.today() and (event.closereg is None or event.closereg > date.today()):
                tmpl = get_template("register.html")
            else:
                tmpl = get_template("regclosed.html")
                events_list = get_all_events(orm_session, 5, hide_closed = True)
            return tmpl.render(event=event, events=events_list, user=u, invite=i)
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
events.connect("register", "/{id}/register/{code}", Events, action="register",
                        conditions={"method":["GET"]})
