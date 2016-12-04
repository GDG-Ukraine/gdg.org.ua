import json
from datetime import date

from sqlalchemy import (
    Column, UnicodeText, Date, String,
    Enum, Boolean, ForeignKey
)

from sqlalchemy.types import TypeDecorator, VARCHAR

from sqlalchemy.dialects.mysql import BIGINT as BigInteger, INTEGER as Integer
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()
metadata = Base.metadata


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
        return json.loads(value) if value is not None else []


__all__ = [
    'WPPost', 'Admin',
    'User', 'Event', 'EventParticipant',
    'Place', 'Invite',
    'EXPERIENCE_CHOICES', 'ENGLISH_CHOICES', 'TSHIRT_CHOICES',
    'GENDER_CHOICES',
]


EXPERIENCE_CHOICES = [
    'newbie', 'elementary', 'intermediate', 'advanced', 'jedi',
]
ENGLISH_CHOICES = [
    'elementary', 'intermediate', 'upper intermediate', 'advanced', 'native',
]
TSHIRT_CHOICES = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
GENDER_CHOICES = ['male', 'female']


class WPPost(Base):
    """WPPost is a view representing Wordpress posts of all groups"""

    __tablename__ = 'gdg_blog_posts_view'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    wp_post_id = Column(BigInteger, primary_key=True)
    post_date = Column(Date)
    post_content = Column(UnicodeText)
    post_title = Column(UnicodeText)
    post_name = Column(String(200))
    guid = Column(String(255))
    comment_count = Column(BigInteger)
    wp_user_id = Column(BigInteger, primary_key=True)
    user_login = Column(String(60), primary_key=True)
    user_nicename = Column(String(50), primary_key=True)
    user_email = Column(String(100), primary_key=True)
    user_status = Column(Integer, primary_key=True)
    display_name = Column(String(250), primary_key=True)
    gdg_place = Column(String(12), primary_key=True)


class Admin(Base):
    """
    This is an admin representation
    """

    __tablename__ = 'gdg_admins'

    def __init__(self, **kwargs):
        super(Admin, self).__init__(**kwargs)

    id = Column(Integer, autoincrement=True, primary_key=True)
    email = Column(String(128), unique=True, nullable=False, index=True)
    filter_place = Column(Integer, ForeignKey('gdg_places.id'),
                          nullable=True, index=True)
    googler_id = Column(Integer, ForeignKey('gdg_participants.id'),
                        nullable=True, index=True)
    godmode = Column(Boolean, default=0, nullable=False)

    place = relationship('Place', backref='admins')


class EventParticipant(Base):
    """
    Class represents a G+ event participant.
    """

    __tablename__ = 'gdg_events_participation'
    __table_args__ = (
        UniqueConstraint('googler_id', 'event_id',
                         name='unique_participation'),
    )

    def __init__(self, **kwargs):
        super(EventParticipant, self).__init__(**kwargs)

    id = Column(Integer, autoincrement=True, primary_key=True)
    googler_id = Column(Integer, ForeignKey('gdg_participants.id'),
                        nullable=False, index=True)
    event_id = Column(Integer, ForeignKey('gdg_events.id'), nullable=False,
                      index=True)

    register_date = Column(Date)

    accepted = Column(Boolean, default=None)
    visited = Column(Boolean, default=None)
    confirmed = Column(Boolean, nullable=False, default=False)

    fields = deferred(Column(JSONEncodedDict(512)))

    user = relationship('User', backref='event_assocs')
    event = relationship('Event', backref='event_assocs')


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
    # Should we accept handles without Full Name?
    nickname = Column(String(45), unique=True, index=True)
    email = Column(String(64), unique=True, nullable=False, index=True)

    phone = Column(String(20), default=None, unique=True, index=True)
    gplus = Column(String(128), default=None, unique=True, index=True)
    hometown = Column(String(30), default=None, index=True)
    company = Column(String(64), default=None, index=True)
    position = Column(String(64), default=None, index=True)
    www = Column(String(100), default=None, unique=True)

    experience_level = Column(
        Enum(*EXPERIENCE_CHOICES, name='experience_level'),
        default=None)
    experience_desc = Column(UnicodeText)
    interests = Column(UnicodeText)

    # TODO: make normal previous/upcoming events DB
    # now it is JSON field.
    events_visited = Column(UnicodeText)
    english_knowledge = Column(
        Enum(*ENGLISH_CHOICES, name='english_knowledge'),
        default=None)
    t_shirt_size = Column(
        Enum(*TSHIRT_CHOICES, name='t_shirt_size'),
        default=None)
    gender = Column(Enum(*GENDER_CHOICES, name='gender'), nullable=False)

    additional_info = deferred(Column(UnicodeText))
    local_gdg_id = Column(Integer, index=True)
    uid = Column(BigInteger)

    # events = relationship("Event", secondary=EventParticipant,
    #                       backref="users")
    events = relationship('EventParticipant',
                          backref='users')

    @property
    def full_name(self):
        if all([self.name, self.surname]):
            return '{name} {surname}'.format(name=self.name,
                                             surname=self.surname)

        for n in ['name', 'nickname', 'surname']:
            if self.__getattribute__(n):
                return self.__getattribute__(n)

        return ''


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
    gplus_event_id = Column(String(27), unique=True, index=True)
    host_gdg_id = Column(Integer, ForeignKey('gdg_places.id'), nullable=False,
                         index=True)

    date = Column(Date)
    closereg = Column(Date)
    fields = deferred(Column(JSONEncodedDict(512)))
    hidden = deferred(Column(JSONEncodedDict(512)))
    # crutch for olostan's code
    background = Column(String(255), nullable=True)
    max_regs = Column(Integer, nullable=True, default=None)
    google_map_iframe = deferred(Column(UnicodeText, nullable=True,
                                        default=None))

    testing = Column(Boolean, nullable=False, default=False)
    require_confirmation = Column(Boolean, nullable=False, default=False)

    participants = relationship('EventParticipant', backref='events')
    host_gdg = relationship('Place', backref='events')

    def has_spots(self):
        """ Checks whether an event has free spots

        Returns:
            (bool): True if there are free spots at event otherwise False
        """
        return self.max_regs is None or self.max_regs > len(self.participants)

    def is_registration_overdue(self):
        """ Checks whether the event registration is overdue
        Event registration is considered overdue when at least one of
        the following conditions are truthy
            - event happens today or has already took place
            - there is an event registration deadline set and it is either
              today or earlier

        Returns:
            (bool): True if event registration is overdue otherwise Flase
        """
        return (
           self.date <= date.today() or
           self.closereg is not None and self.closereg <= date.today()
        )

    def is_registration_open(self):
        """ Event registration is open when there are spots at event and
        event registration is not overdue.
        """
        return self.has_spots() and not self.is_registration_overdue()


class Invite(Base):
    """
    Class represents an event registration invitation code.
    """

    __tablename__ = 'gdg_invites'

    def __init__(self, **kwargs):
        super(Invite, self).__init__(**kwargs)

    code = Column(String(32), autoincrement=True, primary_key=True)
    email = Column(String(64), nullable=True, default=None)
    event_id = Column(Integer, ForeignKey('gdg_events.id'), nullable=False)
    used = Column(Boolean, nullable=False, default=False)

    event = relationship('Event', backref='invites')


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

    show = Column(Enum('1', '0', name='show'), nullable=False, default='0')

    master_id = Column(Integer, ForeignKey('gdg_places.id'), nullable=True,
                       default=None)
    master = relationship('Place', remote_side='Place.id',
                          backref='subdivisions')
