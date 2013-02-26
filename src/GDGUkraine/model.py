import calendar
import os
from base64 import b64decode, b64encode
from datetime import datetime, timedelta
from hashlib import sha256

from sqlalchemy import Column, Integer, UnicodeText, Date, DateTime, String, \
    BigInteger, Enum, SmallInteger, func, text, \
    Boolean
from sqlalchemy.orm import deferred
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()
metadata = Base.metadata


__all__ = ['User', 'Event', 'EventParticipant', 'Place']


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
    name = Column(UnicodeText, nullable=False)
    surname = Column(UnicodeText, nullable=False)
    nickname = Column(UnicodeText, unique=True, index=True) # Should we accept handles without Full Name?
    email = Column(UnicodeText, unique=True, nullable=False, index=True)
    
    phone = Column(UnicodeText, default=None, unique=True, index=True)
    gplus = Column(UnicodeText, default=None, unique=True, index=True)
    hometown = Column(UnicodeText, default=None, index=True)
    company = Column(UnicodeText, default=None, index=True)
    position = Column(UnicodeText, default=None, index=True)
    www = Column(UnicodeText, default=None, unique=True)
        
    experience = Column(Enum('newbie', 'elementary', 'intermediate', 'advanced', 'jedi', name='experience_level'), default=None)
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
    url = Column(UnicodeText, nullable=False)
    title = Column(UnicodeText, nullable=False)
    desc = deferred(Column(UnicodeText, nullable=False))
    gplus_event_id = Column(BigInteger, unique=True, index=True)
    host_gdg_id = Column(Integer, index=True)

    date = Column(Date)


class EventParticipant(Base):
    """
    Class represents a G+ event participant. 
    """

    __tablename__ = 'gdg_events_participation'


    def __init__(self, **kwargs):
        super(EventParticipant, self).__init__(**kwargs)

    id = Column(Integer, autoincrement=True, primary_key=True)
    googler_id = Column(Integer, nullable=False, index=True)
    event_id = Column(Integer, nullable=False, index=True)

    register_date = Column(Date)
    accepted = Column(Boolean)
    visited = Column(Boolean)



class Place(Base):
    """
    Class represents locations GDG's.
    """

    __tablename__ = 'gdg_places'


    def __init__(self, **kwargs):
        super(Place, self).__init__(**kwargs)

    id = Column(Integer, autoincrement=True, primary_key=True)

    city = Column(UnicodeText, nullable=False, default='')
    name = Column(UnicodeText, nullable=True, default=None)
    url = Column(UnicodeText, nullable=False, default='')
    geo = Column(UnicodeText, nullable=False, default='')
    
    show = Column(Enum('1', '0', name="show"), nullable=False, default='0')
