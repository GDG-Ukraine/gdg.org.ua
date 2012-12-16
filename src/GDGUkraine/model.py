import calendar
import os
from base64 import b64decode, b64encode
from datetime import datetime, timedelta
from hashlib import sha256

from sqlalchemy import Column, Integer, UnicodeText, Date, DateTime, String, \
    BigInteger, Enum, SmallInteger, func, text
from sqlalchemy.orm import deferred
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()
metadata = Base.metadata


__all__ = ["User"]


# NOTE: This class is PostgreSQL specific. You should customize age() and the
# character column sizes if you want to use other databases.
class User(Base):
    """
    This example class represents a Facebook user. You can customize this class
    however you want.
    """

    __tablename__ = "user"


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(UnicodeText, nullable=False)
    surname = Column(UnicodeText, nullable=False)
    nickname = Column(UnicodeText, unique=True, index=True)
    email = Column(UnicodeText, unique=True, nullable=False, index=True)

    sex = Column(Enum("m", "f", name="sex"))
    date_of_birth = Column(Date)
    bio = deferred(Column(UnicodeText))

    @hybrid_property
    def age(self):
        """Property calculated from (current time - :attr:`User.date_of_birth` - leap days)"""
        if self.date_of_birth:
            today = (datetime.utcnow() + timedelta(hours=self.timezone)).date()
            birthday = self.date_of_birth
            if isinstance(birthday, datetime):
                birthday = birthday.date()
            age = today - (birthday or (today - timedelta(1)))
            return (age.days - calendar.leapdays(birthday.year, today.year)) / 365
        return -1

    @age.expression
    def age(cls):
        return func.date_part("year", func.age(cls.date_of_birth))

    locale = Column(String(10))
    timezone = Column(SmallInteger)

    created = Column(DateTime, default=datetime.utcnow, server_default=text("now()"), nullable=False)
    lastmodified = Column(DateTime, default=datetime.utcnow, server_default=text("now()"), nullable=False)
    lastaccessed = Column(DateTime, default=datetime.utcnow, server_default=text("now()"), nullable=False)
