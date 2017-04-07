import cherrypy
import logging

from cherrypy import HTTPError  # , HTTPRedirect
from blueberrypy.template_engine import get_template

from .api import (
    get_all_events,  # delete_event_by_id,
    get_n_upcoming_events,
    find_invitation_by_code, find_user_by_email,
    find_event_by_id, find_host_gdg_by_event
)
from .lib.forms import RegistrationForm


logger = logging.getLogger(__name__)


class Events:

    # def create(self, **kwargs):
    #    req = cherrypy.request
    #    orm_session = req.orm_session
    #    event = from_collection(req.json, Event())
    #    orm_session.add(event)
    #    orm_session.commit()
    #    return to_collection(event, sort_keys=True)

    def show(self, id, **kwargs):
        try:
            id = int(id)
            req = cherrypy.request
            orm_session = req.orm_session
            event = find_event_by_id(cherrypy.request.orm_session, id)
            if event:
                tmpl = get_template('event.html')
                return tmpl.render(event=event,
                                   host_gdg=find_host_gdg_by_event(orm_session,
                                                                   event))
            raise HTTPError(404)
        except ValueError:
            raise HTTPError(400, 'Invalid URL')

    def register(self, id, **kwargs):
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        event = find_event_by_id(orm_session, id)
        events_list = None
        u = None
        i = None
        registration_form = None

        if not event:
            # this is is not error, just wrong URL
            logger.info('No event with id=%(id)s was found', {'id': id})
            raise HTTPError(404)

        if kwargs.get('code'):
            i = find_invitation_by_code(orm_session, kwargs['code'])
            if i is None or i.used or i.event_id != event.id:
                # Again it is not an error but a wrong URL param
                logger.info(
                    'Invalid invite code: %(code)s for event %(eid)s',
                    {'code': kwargs['code'], 'eid': id},
                )
                raise HTTPError(403, 'Invalid invite code.')
            if i.email is not None:
                u = find_user_by_email(orm_session, i.email)

        if kwargs.get('code') or event.is_registration_open():
            tmpl = get_template('register.html')
            registration_form = RegistrationForm(event.hidden)
            # Do not use additional_fields_form cause it does not
            # fully support select with custom answer
        else:
            tmpl = get_template('regclosed.html')
            events_list = get_all_events(orm_session, 5, hide_closed=True)

        return tmpl.render(
            host_gdg=find_host_gdg_by_event(orm_session, event),
            event=event, events=events_list,
            user=u, invite=i,
            registration_form=registration_form,
        )

    def list_upcoming(self, **kwargs):
        events = get_n_upcoming_events(
            session=cherrypy.request.orm_session,
            limit=20,
        )
        if events:
            tmpl = get_template('events.html')
            return tmpl.render(events=events)
        raise HTTPError(404)

    def update(self, id, **kwargs):
        id = int(id)
        req = cherrypy.request
        orm_session = req.orm_session
        event = find_event_by_id(orm_session, id)
        if event:
            orm_session.commit()
            return event
        raise HTTPError(404)

    # def delete(self, id, **kwargs):
    #     id = int(id)
    #     req = cherrypy.request
    #     orm_session = req.orm_session
    #     if not delete_event_by_id(orm_session, id):
    #         raise HTTPError(404)
    #     else:
    #         orm_session.commit()


events = cherrypy.dispatch.RoutesDispatcher()
events.mapper.explicit = False
# events.connect("add", "/", Events, action="create",
#                conditions={"method": ["POST"]})
events.connect('list_events', '', Events, action='list_upcoming',
               conditions={'method': ['GET']})
events.connect('list_events', '/', Events, action='list_upcoming',
               conditions={'method': ['GET']})
events.connect('get_event', '/{id}', Events, action='show',
               conditions={'method': ['GET']})
events.connect('edit_event', '/{id}', Events, action='update',
               conditions={'method': ['PUT']})
# events.connect("remove", "/{id}", Events, action="delete",
#                conditions={"method": ["DELETE"]})
events.connect('event_register', '/{id}/register', Events, action='register',
               conditions={'method': ['GET']})
events.connect('event_invite_register', '/{id}/register/{code}',
               Events, action='register',
               conditions={'method': ['GET']})
