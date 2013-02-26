import json

import sys
import traceback

import cherrypy

from cherrypy import HTTPError
from cherrypy.lib import httputil as cphttputil
from blueberrypy.util import from_collection, to_collection

from GDGUkraine import api
from GDGUkraine.model import User, Event, EventParticipant, Place


class Participants:

    _cp_config = {"tools.json_in.on": True}

    @cherrypy.tools.json_out()
    def create(self, **kwargs):
        #return 'creating someone'
        req = cherrypy.request
        orm_session = req.orm_session
        user = from_collection(req.json, User())
        orm_session.add(user)
        orm_session.commit()
        return to_collection(user, sort_keys=True)

    @cherrypy.tools.json_out()
    def show(self, id, **kwargs):
        #return 'getting someone'
        id = int(id)
        user = api.find_user_by_id(cherrypy.request.orm_session, id)
        if user:
            return to_collection(user, excludes=("password", "salt"),
                              sort_keys=True)
        #else:
        #    return {}
        raise HTTPError(404)

    @cherrypy.tools.json_out()
    def update(self, id, **kwargs):
        return 'changing someone'
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        user = api.find_user_by_id(orm_session, id)
        if user:
            user = from_collection(req.json, user)
            orm_session.commit()
            return to_collection(user, includes="age", excludes=("password", "salt"),
                              sort_keys=True)
        raise HTTPError(404)

    def delete(self, id, **kwargs):
        return 'removing someone'
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        if not api.delete_user_by_id(orm_session, id):
            raise HTTPError(404)
        else:
            orm_session.commit()


participants_api = cherrypy.dispatch.RoutesDispatcher()
participants_api.mapper.explicit = False
participants_api.connect("add", "/add", Participants, action="create",
                        conditions={"method":["POST","GET"]})
participants_api.connect("get", "/get/{id}", Participants, action="show",
                        conditions={"method":["POST","GET"]})
participants_api.connect("edit", "/edit/{id}", Participants, action="update",
                        conditions={"method":["POST","GET"]})
participants_api.connect("remove", "/remove/{id}", Participants, action="delete",
                        conditions={"method":["POST","GET"]})

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
