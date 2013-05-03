import json

import sys
import traceback

import cherrypy

from cherrypy import HTTPError
from cherrypy.lib import httputil as cphttputil
from blueberrypy.util import from_collection, to_collection

from GDGUkraine import api
from GDGUkraine.model import User, Event, EventParticipant, Place

from datetime import date, datetime

import logging


logger = logging.getLogger(__name__)

class REST_API_Base:
    _cp_config = {"tools.json_in.on": True}

    def create(self, **kwargs):
        raise NotImplementedError()

    def show(self, **kwargs):
        raise NotImplementedError()

    def list_all(self, **kwargs):
        raise NotImplementedError()

    def update(self, **kwargs):
        raise NotImplementedError()

    def delete(self, **kwargs):
        raise NotImplementedError()

class Participants(REST_API_Base):

    @cherrypy.tools.json_out()
    def create(self, **kwargs):
        #return 'creating someone'
        req = cherrypy.request
        orm_session = req.orm_session
        u = req.json['user']
        logger.debug(req.json)
        logger.debug(u)
        #user = from_collection(u, User())
        user = User(**u)
        logger.debug(user.email)
        eu = api.find_user_by_email(orm_session, user.email)
        if eu:
            user.id = eu.id
        #logger.debug([u for u in dir(user)])
        orm_session.merge(user)
        orm_session.commit()
        if req.json.get('event'):
            eid = int(req.json['event'])
            logger.debug(type(req.json.get('fields')))
            logger.debug(req.json.get('fields'))
            ep = EventParticipant(event_id = eid, googler_id = user.id, register_date = date.today(), fields = req.json['fields'] if req.json.get('fields') else None)
            eep = api.get_event_registration(orm_session, user.id, eid)
            if eep:
                ep.id = eep.id
            logger.debug(ep.fields)
            orm_session.merge(ep)
            orm_session.commit()
            logger.debug(ep.fields)
            logger.debug(type(ep.fields))
        return to_collection(user, sort_keys=True)

    @cherrypy.tools.json_out()
    def show(self, id, **kwargs):
        #return 'getting someone'
        id = int(id)
        user = api.find_user_by_id(cherrypy.request.orm_session, id)
        if user:
            events = api.find_events_by_user(cherrypy.request.orm_session, user)
            logger.debug(events)
            #logger.debug(events[0])
            #logger.debug(events[0].title)
            u = to_collection(user, excludes=("password", "salt"),
                              sort_keys=True)
            u.update({'events': [to_collection(e,
                              sort_keys=True) for e in events]})
            logger.debug(u)
            return u
        #else:
        #    return {}
        raise HTTPError(404)

    @cherrypy.tools.json_out()
    def list_all(self, **kwargs):
        logger.debug('listing users')
        users = api.get_all_users(cherrypy.request.orm_session)
        #return [to_collection(user.serialize) for user in users]
        #x = [u for u in users]
        if users:
            return [to_collection(u, excludes=("password", "salt"),
                              sort_keys=True) for u in users]
        raise HTTPError(404)

    @cherrypy.tools.json_out()
    def update(self, id, **kwargs):
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        user = api.find_user_by_id(orm_session, id)
        if user:
            user = from_collection(req.json, user)
            orm_session.commit()
            return to_collection(user, excludes=("password", "salt"),
                              sort_keys=True)
        raise HTTPError(404)

    def delete(self, id, **kwargs):
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        if not api.delete_user_by_id(orm_session, id):
            raise HTTPError(404)
        else:
            orm_session.commit()

class Events(REST_API_Base):

    @cherrypy.tools.json_out()
    def create(self, **kwargs):
        req = cherrypy.request
        orm_session = req.orm_session
        event = from_collection(req.json, Event())
        orm_session.add(event)
        orm_session.commit()
        return to_collection(event, sort_keys=True)

    @cherrypy.tools.json_out()
    def show(self, id, **kwargs):
        #return 'getting someone'
        id = int(id)
        event = api.find_event_by_id(cherrypy.request.orm_session, id)
        if event:
            participants = api.find_participants_by_event(cherrypy.request.orm_session, event)
            logger.debug(participants)
            logger.debug(participants[0])
            logger.debug(participants[0].name)
            e = to_collection(event,
                    sort_keys=True)
            e.update({'participants': [to_collection(p, excludes=("password", "salt"),
                              sort_keys=True) for p in participants]})
            logger.debug(e)
            return e 
        raise HTTPError(404)

    @cherrypy.tools.json_out()
    def list_all(self, **kwargs):
        events = api.get_all_events(cherrypy.request.orm_session)
        if events:
            return [to_collection(e,
                              sort_keys=True) for e in events]
        raise HTTPError(404)

    @cherrypy.tools.json_out()
    def update(self, id, **kwargs):
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        event = api.find_event_by_id(orm_session, id)
        logger.debug(event)
        if event:
            event = from_collection(req.json, event)
            orm_session.commit()
            return to_collection(event,
                              sort_keys=True)
        raise HTTPError(404)

    def delete(self, id, **kwargs):
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        if not api.delete_event_by_id(orm_session, id):
            raise HTTPError(404)
        else:
            orm_session.commit()

rest_api = cherrypy.dispatch.RoutesDispatcher()
rest_api.mapper.explicit = False
rest_api.connect("add_participant", "/participants", Participants, action="create",
                        conditions={"method":["POST"]})
rest_api.connect("list_participants", "/participants", Participants, action="list_all",
                        conditions={"method":["GET"]})
rest_api.connect("get_participant", "/participants/{id}", Participants, action="show",
                        conditions={"method":["GET"]})
rest_api.connect("edit_participant", "/participants/{id}", Participants, action="update",
                        conditions={"method":["PUT"]})
rest_api.connect("remove_participant", "/participants/{id}", Participants, action="delete",
                        conditions={"method":["DELETE"]})

rest_api.connect("add_event", "/events", Events, action="create",
                        conditions={"method":["POST"]})
rest_api.connect("list_events", "/events", Events, action="list_all",
                        conditions={"method":["GET"]})
rest_api.connect("get_event", "/events/{id}", Events, action="show",
                        conditions={"method":["GET"]})
rest_api.connect("edit_event", "/events/{id}", Events, action="update",
                        conditions={"method":["PUT"]})
rest_api.connect("remove_event", "/events/{id}", Events, action="delete",
                        conditions={"method":["DELETE"]})

# Error handlers

def generic_error_handler(status, message, traceback, version):
    """error_page.default"""
    
    response = cherrypy.response
    response.headers['Content-Type'] = "application/json"
    response.headers.pop('Content-Length', None)

    code, reason, _ = cphttputil.valid_status(status)
    result = {"code": code, "reason": reason, "message": message}
    if hasattr(cherrypy.request, "params"):
        params = cherrypy.request.params
        if "debug" in params and params["debug"]:
            result["traceback"] = traceback
    return json.dumps(result)

def unexpected_error_handler():
    """request.error_response"""

    (typ, value, tb) = sys.exc_info()
    if typ:
        debug = False
        if hasattr(cherrypy.request, "params"):
            params = cherrypy.request.params
            debug = "debug" in params and params["debug"]

        response = cherrypy.response
        response.headers['Content-Type'] = "application/json"
        response.headers.pop('Content-Length', None)
        content = {}

        if isinstance(typ, HTTPError):
            cherrypy._cperror.clean_headers(value.code)
            response.status = value.status
            content = {"code": value.code, "reason": value.reason, "message": value._message}
        elif isinstance(typ, (TypeError, ValueError, KeyError)):
            cherrypy._cperror.clean_headers(400)
            response.status = 400
            reason, default_message = cphttputil.response_codes[400]
            content = {"code": 400, "reason": reason, "message": value.message or default_message}

        if cherrypy.serving.request.show_tracebacks or debug:
            tb = traceback.format_exc()
            content["traceback"] = tb
        response.body = json.dumps(content)
