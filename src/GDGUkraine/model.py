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
    fbid = Column(BigInteger, unique=True, index=True)
    username = Column(UnicodeText, unique=True, index=True)
    displayname = Column(UnicodeText, nullable=False)
    email = Column(UnicodeText, unique=True, nullable=False, index=True)

    _salt = Column("salt", String(12))

    @hybrid_property
    def salt(self):
        """Generates a cryptographically random salt and sets its Base64 encoded
        version to the salt column, and returns the encoded salt.
        """
        if not self.id and not self._salt:
            self._salt = b64encode(os.urandom(8))

        return self._salt

    # 64 is the length of the SHA-256 encoded string length
    _password = Column("password", String(64))

    def __encrypt_password(self, password, salt):
        """
        Encrypts the password with the given salt using SHA-256. The salt must
        be cryptographically random bytes.

        :param password: the password that was provided by the user to try and
                         authenticate. This is the clear text version that we
                         will need to match against the encrypted one in the
                         database.
        :type password: basestring

        :param salt: the salt is used to strengthen the supplied password
                     against dictionary attacks.
        :type salt: an 8-byte long cryptographically random byte string
        """

        if isinstance(password, str):
            password_bytes = password.encode("UTF-8")
        else:
            password_bytes = password

        hashed_password = sha256()
        hashed_password.update(password_bytes)
        hashed_password.update(salt)
        hashed_password = hashed_password.hexdigest()

        if not isinstance(hashed_password, str):
            hashed_password = hashed_password.decode("UTF-8")

        return hashed_password

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = self.__encrypt_password(password,
                                                 b64decode(str(self.salt)))

    def validate_password(self, password):
        """Check the password against existing credentials.

        :type password: unicode
        :param password: clear text password
        :rtype: bool
        """
        return self.password == self.__encrypt_password(password,
                                                        b64decode(str(self.salt)))

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
