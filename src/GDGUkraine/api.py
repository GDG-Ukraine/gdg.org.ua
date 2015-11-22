import logging

from GDGUkraine.model import (Admin, User,
                              Event, EventParticipant,
                              Place, Invite)
from datetime import date, datetime


logger = logging.getLogger(__name__)


def find_user_by_id(session, id):
    id = int(id)
    return session.query(User).get(id)

def find_user_by_email(session, email):
    q = session.query(User)\
        .filter(User.email == email)
    return q.first()

def find_admin_by_email(session, email):
    q = session.query(Admin)\
        .filter(Admin.email == email)
    return q.first()

def delete_user_by_id(session, id):
    id = int(id)
    return session.query(User).filter(User.id == id).delete()

def get_all_users(session):
    return session.query(User).all()

def get_all_gdg_places(session, filtered = False):
    q = session.query(Place)
    if filtered:
        q = q.filter(Place.show=='1')
    return q.order_by(Place.city).all()

def find_event_by_id(session, id):
    id = int(id)
    return session.query(Event).get(id)

def find_host_gdg_by_event(session, event):
    try:
        id = int(id)
        return session.query(Event).get(id)
    except:
        return None

def get_all_events(session, lim = None, hide_closed = False):
    q = session.query(Event).order_by(Event.date)
    if hide_closed:
        q = q.filter(Event.closereg > date.today())
    if lim:
        q = q.limit(lim)
    return q.all()

def delete_event_by_id(session, id):
    id = int(id)
    return session.query(Event).filter(Event.id == id).delete()

def find_participants_by_event(session, e):
    return session.query(User).join(EventParticipant.users).join(EventParticipant.events).filter(e.id == EventParticipant.event_id).all()

def find_events_by_user(session, u):
    return session.query(Event).join(EventParticipant.events).join(EventParticipant.users).filter(u.id == EventParticipant.googler_id).all()

def get_event_registration(session, uid, eid):
    q = session.query(EventParticipant)\
        .filter(uid == EventParticipant.googler_id)\
        .filter(eid == EventParticipant.event_id)
    return q.first()

def get_event_registrations(session, event_id):
    return session.query(EventParticipant).filter(event_id == EventParticipant.event_id).all()

def find_invitation_by_code(session, code):
    q = session.query(Invite)\
        .filter(Invite.code == code)
    return q.first()
