import calendar
import os
from base64 import b64decode, b64encode
from datetime import datetime, timedelta
from hashlib import sha256

from sqlalchemy import Column, Integer, UnicodeText, Date, DateTime, String, \
    BigInteger, Enum, SmallInteger, func, text, \
    Boolean, ForeignKey
from sqlalchemy.orm import deferred, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()
metadata = Base.metadata

from sqlalchemy.types import TypeDecorator, VARCHAR
import json

class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedDict(255)

    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

__all__ = ['User', 'Event', 'EventParticipant', 'Place']


class EventParticipant(Base):
    """
    Class represents a G+ event participant. 
    """

    __tablename__ = 'gdg_events_participation'
    __table_args__ = (UniqueConstraint('googler_id', 'event_id', name='unique_participation'),
                     )


    def __init__(self, **kwargs):
        super(EventParticipant, self).__init__(**kwargs)

    id = Column(Integer, autoincrement=True, primary_key=True)
    googler_id = Column(Integer, ForeignKey('gdg_participants.id'), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey('gdg_events.id'), nullable=False, index=True)

    register_date = Column(Date)
    accepted = Column(Boolean, default = None)
    visited = Column(Boolean, default = None)
    fields = deferred(Column(JSONEncodedDict(512)))

    users = relationship("User", backref="event_assocs")
    events = relationship("Event", backref="event_assocs")


# NOTE: This class is PostgreSQL specific. You should customize age() and the
# character column sizes if you want to use other databases.
class User(Base):
    """
    This example class represents a Facebook user. You can customize this class
    however you want.
    """

    __tablename__ = 'gdg_participants'


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(35), nullable=False)
    surname = Column(String(35), nullable=False)
    nickname = Column(String(45), unique=True, index=True) # Should we accept handles without Full Name?
    email = Column(String(64), unique=True, nullable=False, index=True)
    
    phone = Column(String(20), default=None, unique=True, index=True)
    gplus = Column(String(128), default=None, unique=True, index=True)
    hometown = Column(String(30), default=None, index=True)
    company = Column(String(64), default=None, index=True)
    position = Column(String(25), default=None, index=True)
    www = Column(String(100), default=None, unique=True)
        
    experience_level = Column(Enum('newbie', 'elementary', 'intermediate', 'advanced', 'jedi', name='experience_level'), default=None)
    experience_desc = Column(UnicodeText)
    interests = Column(UnicodeText)
    
    events_visited = Column(UnicodeText) # TODO: make normal previous/upcoming events DB\nnow it is JSON field.
    english_knowledge = Column(Enum('elementary', 'intermediate', 'upper intermediate', 'advanced', 'native', name="english_knowledge"), default=None)
    t_shirt_size = Column(Enum('S', 'M', 'L', 'XL', 'XXL', name="t_shirt_size"), default=None)
    gender = Column(Enum('male', 'female', name="gender"), nullable=False)
    
    additional_info = deferred(Column(UnicodeText))
    local_gdg_id = Column(Integer, index=True)
    uid = Column(BigInteger)


class Event(Base):
    """
    Class represents a G+ event. 
    """

    __tablename__ = 'gdg_events'


    def __init__(self, **kwargs):
        super(Event, self).__init__(**kwargs)

    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(String(64), nullable=False)
    title = Column(String(64), nullable=False)
    desc = deferred(Column(UnicodeText, nullable=False))
    gplus_event_id = Column(BigInteger, unique=True, index=True)
    host_gdg_id = Column(Integer, ForeignKey('gdg_places.id'), nullable=False, index=True)

    date = Column(Date)
    closereg = Column(Date)
    fields = deferred(Column(JSONEncodedDict(512)))
    # crutch for olostan's code
    background = Column(String(255), nullable=True)
    max_regs = Column(Integer, nullable=True, default=None)

    participants = relationship("EventParticipant", backref="event")
    host_gdg = relationship("Place", backref="events")


class Place(Base):
    """
    Class represents locations GDG's.
    """

    __tablename__ = 'gdg_places'


    def __init__(self, **kwargs):
        super(Place, self).__init__(**kwargs)

    id = Column(Integer, autoincrement=True, primary_key=True)

    city = Column(String(20), nullable=False, default='')
    name = Column(String(20), nullable=True, default=None)
    url = Column(String(50), nullable=False, default='')
    geo = Column(String(30), nullable=False, default='')
    logo = Column(String(255), nullable=True, default=None)
    
    show = Column(Enum('1', '0', name="show"), nullable=False, default='0')
