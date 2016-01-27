import json

import sys
import traceback
import re

import cherrypy

from cherrypy import HTTPError
from cherrypy.lib import httputil as cphttputil, file_generator
from blueberrypy.util import from_collection, to_collection

from .table_exporter import TableExporter

from . import api
from .model import User, Event, EventParticipant
from .auth_controller import client_id as google_client_id, OAuth2Session
from .utils import gmail_send_html, aes_encrypt, make_vcard

from datetime import date

import logging


logger = logging.getLogger(__name__)


class APIBase:
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


class Admin(APIBase):
    @cherrypy.tools.json_out()
    @cherrypy.tools.authorize()
    def info(self):
        req = cherrypy.request
        user = {'admin': True}
        user.update(req.admin_user)
        user.update(req.google_user)
        user.update(req.google_oauth_token)
        res = {'user': user}
        if user.get('filter_place'):
            res['place'] = to_collection(
                api.get_place_by_id(
                    cherrypy.request.orm_session,
                    req.admin_user['filter_place']))
        return res


class Participants(APIBase):

    @cherrypy.tools.json_out()
    def create(self, **kwargs):
        req = cherrypy.request
        orm_session = req.orm_session
        u = req.json['user']
        logger.debug(req.json)
        logger.debug(u)
        user = User(**u)
        eu = api.find_user_by_email(orm_session, user.email)
        if eu:
            user.id = eu.id
            orm_session.merge(user)
        else:
            orm_session.add(user)
        orm_session.commit()
        if req.json.get('event'):
            eid = int(req.json['event'])
            # check if the invitation is valid
            i = None
            if req.json.get('invite_code'):
                i = api.find_invitation_by_code(orm_session,
                                                req.json['invite_code'])
                if i is None or i.used or \
                        (i.event is not None and
                            i.event != api.find_event_by_id(
                                orm_session,
                                req.json['event'])) or \
                        (i.email is not None and i.email != user.email):
                    raise HTTPError(403, "Invalid invite code.")
            logger.debug(type(req.json.get('fields')))
            logger.debug(req.json.get('fields'))
            eep = api.get_event_registration(orm_session, user.id, eid)
            ep = EventParticipant(
                id=eep.id if eep else None, event_id=eid, googler_id=user.id,
                register_date=date.today(),
                fields=req.json['fields'] if req.json.get('fields') else None)
            logger.debug(ep.fields)
            if eep:
                orm_session.merge(ep)
            else:
                orm_session.add(ep)
            if i is not None:
                i.email = user.email
                i.used = True
                orm_session.merge(i)
            orm_session.commit()
            logger.debug(ep.fields)
            logger.debug(type(ep.fields))
        return to_collection(user, sort_keys=True)

    @cherrypy.tools.json_out()
    @cherrypy.tools.authorize()
    def show(self, id, **kwargs):
        id = int(id)
        user = api.find_user_by_id(cherrypy.request.orm_session, id)
        if user:
            events = api.find_events_by_user(cherrypy.request.orm_session,
                                             user)
            logger.debug(events)
            u = to_collection(user, excludes=("password", "salt"),
                              sort_keys=True)
            u.update({'events': [
                to_collection(e, sort_keys=True) for e in events]})
            logger.debug(u)
            return u
        raise HTTPError(404)

    @cherrypy.tools.json_out()
    @cherrypy.tools.authorize()
    def list_all(self, **kwargs):
        logger.debug('listing users')
        users = api.get_all_users(cherrypy.request.orm_session)
        if users:
            return [to_collection(
                u, excludes=("password", "salt"), sort_keys=True)
                for u in users]
        raise HTTPError(404)

    @cherrypy.tools.json_out()
    @cherrypy.tools.authorize()
    def update(self, id, **kwargs):
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        user = api.find_user_by_id(orm_session, id)
        if user:
            user = from_collection(req.json, user)
            orm_session.merge(user)
            orm_session.commit()
            return to_collection(user, excludes=("password", "salt"),
                                 sort_keys=True)
        raise HTTPError(404)

    @cherrypy.tools.authorize()
    def delete(self, id, **kwargs):
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        if not api.delete_user_by_id(orm_session, id):
            raise HTTPError(404)
        else:
            orm_session.commit()


class Events(APIBase):

    @cherrypy.tools.json_out()
    @cherrypy.tools.authorize()
    def create(self, **kwargs):
        req = cherrypy.request
        orm_session = req.orm_session
        event = from_collection(req.json, Event())
        orm_session.add(event)
        orm_session.commit()
        return to_collection(event, sort_keys=True)

    @cherrypy.tools.json_out()
    @cherrypy.tools.authorize()
    def show(self, id, **kwargs):
        id = int(id)
        event = api.find_event_by_id(cherrypy.request.orm_session, id)
        if event:
            registrations = api.get_event_registrations(
                cherrypy.request.orm_session, event.id)
            logger.debug(registrations)
            e = to_collection(event, sort_keys=True)
            e.update({'registrations': [to_collection(r, sort_keys=True)
                     for r in registrations]})
            for r in e['registrations']:
                r.update({'participant': to_collection(
                    api.find_user_by_id(cherrypy.request.orm_session,
                                        r['googler_id']),
                    excludes=("password", "salt"))})
            logger.debug(e)
            return e
        raise HTTPError(404)

    @cherrypy.tools.json_out()
    @cherrypy.tools.authorize()
    def list_all(self, **kwargs):
        events = api.get_all_events(cherrypy.request.orm_session)
        if events:
            return [to_collection(e, sort_keys=True)
                    for e in events]
        raise HTTPError(404)

    @cherrypy.tools.json_out()
    @cherrypy.tools.authorize()
    def update(self, id, **kwargs):
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        event = api.find_event_by_id(orm_session, id)
        logger.debug(event)
        if event:
            # Caution! crunches ahead
            event = from_collection(req.json, event,
                                    excludes=['fields'])  # skip jsonencoded
            # since 'hidden' is not implemented in the model, skip it for now
            event.fields = req.json['fields']  # and set them manually
            orm_session.merge(event)
            orm_session.commit()
            return to_collection(event, sort_keys=True)
        raise HTTPError(404)

    @cherrypy.tools.authorize()
    def delete(self, id, **kwargs):
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        if not api.delete_event_by_id(orm_session, id):
            raise HTTPError(404)
        else:
            orm_session.commit()

    @cherrypy.tools.json_out()
    @cherrypy.tools.authorize()
    def approve_participants(self, id, **kwargs):
        '''POST /api/events/:id/approve'''
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        try:
            oauth2session = OAuth2Session(
                google_client_id(),
                token=cherrypy.session['google_oauth_token'])
            regs = req.json.get('registrations')
            from_email = (req.json.get('fromEmail') or
                          'GDG Registration Robot <kyiv@gdg.org.ua>')
            send_email = req.json.get('sendEmail')

            subject = '✔ Registration confirmation to {event_title}'
            to_email = '{full_name} <{email}>'
            email_template = 'email/card.html'

            event = api.find_event_by_id(orm_session, id)

            for user_reg in api.get_event_registrations_by_ids(
                    orm_session, [int(_) for _ in regs]):

                u = user_reg.user
                user_reg.accepted = True

                orm_session.merge(user_reg)
                orm_session.commit()

                if send_email:  # Do send email here
                    gmail_send_html(
                        oauth2session,
                        template=email_template,
                        payload={'event': event, 'user': u,
                                 'registration': user_reg,
                                 'qrdata': make_vcard(user_reg)},
                        sbj=subject.format(event_title=event.title),
                        to_email=to_email.format(full_name=u.full_name,
                                                 email=u.email),
                        from_email=from_email)
        except KeyError:
            logger.exception('Could not send confirmation request')
            raise HTTPError(400, {'ok': False})
        else:
            return {'ok': True}

    @cherrypy.tools.json_out()
    @cherrypy.tools.authorize()
    def send_confirm_participants(self, id, **kwargs):
        '''POST /api/events/:id/send-confirm'''
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        try:
            oauth2session = OAuth2Session(
                google_client_id(),
                token=cherrypy.session['google_oauth_token'])
            regs = req.json.get('registrations')
            from_email = (req.json.get('fromEmail') or
                          'GDG Registration Robot <kyiv@gdg.org.ua>')

            subject = 'Please confirm your visit to {event_title}'
            to_email = '{full_name} <{email}>'
            email_template = 'email/confirmation.html'

            event = api.find_event_by_id(orm_session, id)

            for user_reg in api.get_event_registrations_by_ids(
                    orm_session, [int(_) for _ in regs]):
                logger.debug(user_reg)
                u = user_reg.user

                secure_id = aes_encrypt(str(user_reg.id))

                confirm_data = {
                    'url': '/confirm/{id}'.format(id=secure_id)
                }
                logger.debug(confirm_data)

                # Do send email here
                gmail_send_html(
                    oauth2session,
                    template=email_template,
                    payload={'event': event, 'user': u,
                             'registration': user_reg,
                             'confirm': confirm_data},
                    sbj=subject.format(event_title=event.title),
                    to_email=to_email.format(full_name=u.full_name,
                                             email=u.email),
                    from_email=from_email)
        except KeyError:
            logger.exception('Could not send confirmation request')
            raise HTTPError(400, "{'ok': False}")
        else:
            return {'ok': True}

    @cherrypy.tools.json_out()
    @cherrypy.tools.authorize()
    def resend_approve_participants(self, id, **kwargs):
        '''POST /api/events/:id/resend'''
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        try:
            oauth2session = OAuth2Session(
                google_client_id(),
                token=cherrypy.session['google_oauth_token'])
            user_id = int(req.json.get('id'))
            from_email = (req.json.get('fromEmail') or
                          'GDG Registration Robot <kyiv@gdg.org.ua>')

            subject = '✔ Registration confirmation to {event_title}'
            to_email = '{full_name} <{email}>'
            email_template = 'email/card.html'

            user_reg = api.get_event_registration(orm_session, user_id, id)
            event = user_reg.event
            user = user_reg.user

            gmail_send_html(
                oauth2session,
                template=email_template,
                payload={'event': event, 'user': user,
                         'registration': user_reg},
                sbj=subject.format(event_title=event.title),
                to_email=to_email.format(full_name=user.full_name,
                                         email=user.email),
                from_email=from_email)
        except KeyError:
            raise HTTPError(400, {'ok': False})
        else:
            return {'ok': True}

    @cherrypy.tools.authorize()
    def export_participants(self, id):
        """Exports xlsx file with event participants

        Args:
            id (int): event id
        """
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        event = api.find_event_by_id(orm_session, id)
        if event is None:
            raise HTTPError(404)
        participations = api.find_participants_by_event(orm_session, event)
        exporter = TableExporter(
            data=participations,
            data_getters=[
                (lambda x: x.EventParticipant.id),
                (lambda x: x.EventParticipant.register_date),
                (lambda x: id),
                (lambda x: event.title),
                (lambda x: x.User.full_name),
                (lambda x: x.User.gender),
                (lambda x: x.User.nickname or ''),
                (lambda x: x.User.email),
                (lambda x: x.User.phone or ''),
                (lambda x: x.User.gplus),
                (lambda x: x.User.hometown or ''),
                (lambda x: x.User.company or ''),
                (lambda x: x.User.position or ''),
                (lambda x: x.User.www or ''),
                (lambda x: x.User.experience_level or ''),
                (lambda x: x.User.experience_desc or ''),
                (lambda x: x.User.interests or ''),
                (lambda x: x.User.events_visited or ''),
                (lambda x: x.User.english_knowledge or ''),
                (lambda x: x.User.t_shirt_size or ''),
                (lambda x: x.User.additional_info or ''),
                (lambda x: (
                    json.dumps(x.EventParticipant.fields)
                    if x.EventParticipant.fields
                    else ''
                )),
                (lambda x: x.EventParticipant.confirmed),
            ],
            headers=[
                'Registration id',
                'Registration date',
                'Event id',
                'Event title',
                'Name',
                'Gender',
                'Nickname',
                'Email',
                'Phone',
                'Google +',
                'City',
                'Company',
                'Position',
                'Website',
                'Experience level',
                'Experience description',
                'Interests',
                'Events visited',
                'English knowledge',
                'T-Shirt size',
                'Additional info',
                'Extra fields',
                'Confirmed',
            ],
        )
        cherrypy.response.headers['Content-Type'] = (
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = re.compile(r'[^\w-]').sub('', event.title.replace(' ', '_'))
        cherrypy.response.headers['Content-Disposition'] = (
            'attachment; filename={}-{}-{}-participants.xlsx'.format(
                event.id, filename, event.date,
            )
        )
        return file_generator(exporter.get_xlsx_content())


class Places(APIBase):
    @cherrypy.tools.json_out()
    def list_all(self, **kwargs):
        places = api.get_all_gdg_places(cherrypy.request.orm_session)
        if places:
            return [to_collection(p, sort_keys=True) for p in places]
        raise HTTPError(404)

rest_api = cherrypy.dispatch.RoutesDispatcher()
rest_api.mapper.explicit = False
rest_api.connect("add_participant", "/participants", Participants,
                 action="create", conditions={"method": ["POST"]})
rest_api.connect("list_participants", "/participants", Participants,
                 action="list_all", conditions={"method": ["GET"]})
rest_api.connect("get_participant", "/participants/{id}", Participants,
                 action="show", conditions={"method": ["GET"]})
rest_api.connect("edit_participant", "/participants/{id}", Participants,
                 action="update", conditions={"method": ["PUT"]})
# rest_api.connect("remove_participant", "/participants/{id}", Participants,
#                  action="delete", conditions={"method": ["DELETE"]})

rest_api.connect("api_add_event", "/events", Events, action="create",
                 conditions={"method": ["POST"]})
rest_api.connect("api_list_events", "/events", Events, action="list_all",
                 conditions={"method": ["GET"]})
rest_api.connect("api_get_event", "/events/{id}", Events, action="show",
                 conditions={"method": ["GET"]})
rest_api.connect("api_edit_event", "/events/{id}", Events, action="update",
                 conditions={"method": ["PUT"]})
# rest_api.connect("remove_event", "/events/{id}", Events, action="delete",
#                  conditions={"method": ["DELETE"]})

rest_api.connect("approve_event_participants",
                 r"/events/{id:\d+}/approve", Events,
                 action="approve_participants",
                 conditions={"method": ["POST"]})
rest_api.connect("send_confirm_event_participants",
                 r"/events/{id:\d+}/send-confirm", Events,
                 action="send_confirm_participants",
                 conditions={"method": ["POST"]})
rest_api.connect("resend_approve_event_participants",
                 r"/events/{id:\d+}/resend", Events,
                 action="resend_approve_participants",
                 conditions={"method": ["POST"]})
rest_api.connect("export_event_participants",
                 r"/events/{id:\d+}/export_participants", Events,
                 action="export_participants",
                 conditions={"method": ["GET"]})

rest_api.connect("list_places", "/places", Places, action="list_all",
                 conditions={"method": ["GET"]})

rest_api.connect("api_info", "/info", Admin, action="info",
                 conditions={"method": ["GET"]})


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
            content = {"code": value.code, "reason": value.reason,
                       "message": value._message}
        elif isinstance(typ, (TypeError, ValueError, KeyError)):
            cherrypy._cperror.clean_headers(400)
            response.status = 400
            reason, default_message = cphttputil.response_codes[400]
            content = {"code": 400, "reason": reason,
                       "message": value.message or default_message}

        if cherrypy.serving.request.show_tracebacks or debug:
            tb = traceback.format_exc()
            content["traceback"] = tb
        response.body = json.dumps(content)
