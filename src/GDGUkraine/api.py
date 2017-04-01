import logging

from GDGUkraine.model import (
    Admin, User,
    Event, EventParticipant,
    Place, Invite, WPPost,
)
from datetime import date


logger = logging.getLogger(__name__)


def get_all_posts(session, offset=0, lim=10):
    q = session.query(WPPost).order_by(-WPPost.post_date)
    return q.offset(offset).limit(lim).all()


def get_place_by_id(session, id):
    id = int(id)
    return session.query(Place).get(id)


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


def get_users_by_ids(session, ids):
    return session.query(User).filter(User.id.in_(ids)).all()


def get_event_registrations_by_ids(session, reg_ids):
    return session.query(EventParticipant)\
        .filter(EventParticipant.id.in_(reg_ids)).all()


def get_event_registration_by_id(session, reg_id):
    return session.query(EventParticipant).get(reg_id)


def get_all_gdg_places(session, filtered=False):
    q = session.query(Place)
    if filtered:
        q = q.filter(Place.show == '1')
    return q.order_by(Place.city).all()


def find_event_by_id(session, id_):
    # correctness of id_ is a matter of the caller
    return session.query(Event).get(id_)


def find_host_gdg_by_event(session, event):
    try:
        id = int(id)
        return session.query(Event).get(id)
    except:
        return None


def get_all_events(session, lim=None, hide_closed=False):
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
    return (
        session.query(User, EventParticipant, Event)
        .join(EventParticipant, EventParticipant.googler_id == User.id)
        .join(Event, EventParticipant.event_id == Event.id)
        .filter(e.id == EventParticipant.event_id)
        .all()
    )


def find_events_by_user(session, u):
    return session.query(Event)\
        .join(EventParticipant.events).join(EventParticipant.users)\
        .filter(u.id == EventParticipant.googler_id).all()


def get_event_registration(session, uid, eid):
    q = session.query(EventParticipant)\
        .filter(uid == EventParticipant.googler_id)\
        .filter(eid == EventParticipant.event_id)
    return q.first()


def get_event_registrations(session, event_id):
    return session.query(EventParticipant)\
        .filter(event_id == EventParticipant.event_id).all()


def find_invitation_by_code(session, code):
    q = session.query(Invite)\
        .filter(Invite.code == code)
    return q.first()
