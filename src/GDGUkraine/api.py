import logging

from GDGUkraine.model import User


logger = logging.getLogger(__name__)


def find_user_by_id(session, id):
    id = int(id)
    return session.query(User).get(id)

def find_user_by_email(session, email):
    q = session.query(User)\
        .filter(User.email == email)
    return q.first()

def delete_user_by_id(session, id):
    id = int(id)
    return session.query(User).filter(User.id == id).delete()